from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
import json
from uuid import uuid4
from httpx import AsyncClient, HTTPError

import logfire
from redis import Redis

from core.exceptions import InvalidRequest, MissingResource
from crud.chat import CRUDChat, CRUDSession
from crud.currency import CRUDUserCurrency
from crud.transaction import CRUDTransaction
from schemas.ai_schemas import Interpretation, NLResolveResult
from schemas.chat import ChatMessageCreate, SessionChatCreate
from schemas.enums import ChatRoleEnum
from utils.currency_conversion import from_minor_units
from utils.helper import convert_sql_models_to_dict
from core import settings


class AIInsightService:
    def __init__(
        self,
        crud_transaction: CRUDTransaction,
        crud_user_currency: CRUDUserCurrency,
        crud_chat: CRUDChat,
        crud_session: CRUDSession,
        redis_client: Redis,
    ):
        self.http_client = AsyncClient(base_url=settings.AI_SERVICE_URL, timeout=600.0)
        self.crud_transaction = crud_transaction
        self.crud_user_currency = crud_user_currency
        self.crud_chat = crud_chat
        self.crud_session = crud_session
        self.redis_client = redis_client

    async def create_session(self, user_id: int):
        session_id = str(user_id) + "-" + str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        session_obj = SessionChatCreate(
            user_id=user_id,
            session_id=session_id,
            expires_at=expires_at,
        )
        session = self.crud_session.create(session_obj)

        return session

    async def interpret_insight(
        self,
        query: str,
        user_id: int,
        session_id: str,
    ):
        query_plan = await self.get_last_query_plan(
            user_id=user_id, session_id=session_id
        )

        # Validate session exists
        await self._validate_session(user_id, session_id)

        # Save user message
        await self.save_message(
            user_id=user_id,
            content=query,
            role=ChatRoleEnum.USER,
            session_id=session_id,
            llm_model=settings.LLM_PROVIDER,
        )

        response = await self.http_client.post(
            "/nl/interpret",
            json={
                "query": query,
                "user_id": user_id,
                "query_plan": query_plan,
            },
            headers={"monetra-ai-key": settings.BACKEND_HEADER},
            params={"llm_provider": settings.LLM_PROVIDER},
        )

        if response.status_code != 200:
            raise InvalidRequest(message="Unable to interpret insight query")

        rsp = Interpretation(**response.json())

        if rsp.explanation_request == False and rsp.delta.target_kind != None:
            logfire.info(
                f"Querying insight for user_id: {user_id} with explanation_request={rsp.explanation_request} and intent={rsp.delta.intent}"
            )
            payload = await self.prepare_insight(
                query=query,
                user_id=user_id,
                session_id=session_id,
                query_plan=rsp.delta.model_dump(),
            )

            stream = self.query_insight(
                payload=payload, user_id=user_id, session_id=session_id
            )
        else:
            logfire.info(
                f"Generating explanation for user_id: {user_id} with explanation_request={rsp.explanation_request}"
            )
            stream = self.explain_insight(
                query=query,
                user_id=user_id,
                query_plan=query_plan,
                session_id=session_id,
            )

        return stream

    async def prepare_insight(
        self, query: str, user_id: int, session_id: str, query_plan: dict
    ) -> dict:
        """Prepare insight payload by resolving query and processing transactions."""
        logfire.info(f"Using: {settings.LLM_PROVIDER} from the backend")

        # Resolve the query
        rsp = await self._resolve_query(query, user_id, query_plan)

        # Cache the resolve result
        self._cache_resolve_result(rsp, user_id, session_id)

        # Fetch and prepare transactions
        _, total_transactions_amount = self._fetch_and_prepare_transactions(
            category_id=rsp.resolved_category_id, user_id=user_id, session_id=session_id
        )

        # Get currency code
        currency_code = self._get_currency_code(user_id)

        # Build payload
        payload = self._build_insight_payload(
            rsp=rsp,
            query=query,
            total_amount=total_transactions_amount,
            currency_code=currency_code,
        )

        logfire.info(f"Prepared insight payload: {payload} for user_id: {user_id}")
        return payload

    async def query_insight(self, payload: dict, user_id: int, session_id: str):
        # Stream the response
        try:
            async with self.http_client.stream(
                "POST",
                "nl/format",
                json=payload,
                headers={"monetra-ai-key": settings.BACKEND_HEADER},
                params={"llm_provider": settings.LLM_PROVIDER},
            ) as rsp:
                rsp.raise_for_status()

                text = ""
                async for line in rsp.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        # print("Sending line:", line)
                        text += line[6:]  # Remove "data: " prefix
                        yield line + " " + "\n\n"

                await self.save_message(
                    user_id=user_id,
                    content=text,
                    role=ChatRoleEnum.ASSISTANT,
                    session_id=session_id,
                    llm_model=settings.LLM_PROVIDER,
                )
        except HTTPError:
            yield "data: Unable to format insight response.\n\n"

    async def explain_insight(
        self, query: str, user_id: int, query_plan: dict, session_id: str
    ):
        messages = await self.get_message_history_for_ai_context(
            user_id=user_id, session_id=session_id
        )
        results = await self.get_transactions_for_insight(
            user_id=user_id, session_id=session_id
        )
        message_list = [convert_sql_models_to_dict(m) for m in messages]
        for m in message_list:
            m["created_at"] = m["created_at"].isoformat()

        message_list_json = json.dumps(message_list)

        try:
            async with self.http_client.stream(
                "POST",
                "nl/explain",
                json={
                    "query": query,
                    "user_id": user_id,
                    "query_plan": query_plan,
                    "message_list": message_list_json,
                    "result_summary": results,
                },
                headers={"monetra-ai-key": settings.BACKEND_HEADER},
                params={"llm_provider": settings.LLM_PROVIDER},
            ) as rsp:
                rsp.raise_for_status()

                text = ""
                async for line in rsp.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        text += line[6:]
                        yield line + " " + "\n\n"

                await self.save_message(
                    user_id=user_id,
                    session_id=session_id,
                    role=ChatRoleEnum.ASSISTANT,
                    content=text,
                    llm_model=settings.LLM_PROVIDER,
                )

        except HTTPError:
            rsp = "data: Unable to explain insight response.\n\n"
            yield rsp

    async def _resolve_query(
        self, query: str, user_id: int, query_plan: dict
    ) -> NLResolveResult:
        """Call the NL resolve endpoint and return the result."""
        response = await self.http_client.post(
            "/nl/resolve",
            json={"query": query, "user_id": user_id, "query_plan": query_plan},
            headers={"monetra-ai-key": settings.BACKEND_HEADER},
            params={"llm_provider": settings.LLM_PROVIDER},
        )

        if response.status_code != 200:
            raise InvalidRequest(message="Unable to resolve insight query")

        rsp = NLResolveResult(**response.json())

        if not rsp.ok:
            raise InvalidRequest(message="Unable to resolve insight query")

        if rsp.resolved_category_id is None:
            raise InvalidRequest(message="No category resolved for the query")

        return rsp

    async def _validate_session(self, user_id: int, session_id: str) -> None:
        """Validate that the session exists for the user."""
        if not self.crud_session.get_session_by_session_id(
            session_id=session_id, user_id=user_id
        ):
            logfire.warning(
                f"Session ID not found for user_id: {user_id} with session_id: {session_id}"
            )
            raise MissingResource(message="Session ID not found")

    def _cache_resolve_result(
        self, rsp: NLResolveResult, user_id: int, session_id: str
    ) -> None:
        """Cache the resolve result in Redis."""
        self.redis_client.set(
            f"ai_insight:{user_id}:{session_id}",
            json.dumps(rsp.model_dump()),
            ex=3600,
        )

    def _serialize_transaction_dates(self, tx: dict) -> None:
        """Convert datetime objects in transaction to ISO format strings."""
        tx["created_at"] = tx["created_at"].isoformat()
        tx["updated_at"] = tx["updated_at"].isoformat() if tx["updated_at"] else None
        tx["date"] = tx["date"].isoformat() if tx["date"] else None
        tx["category"]["created_at"] = tx["category"]["created_at"].isoformat()
        tx["category"]["updated_at"] = (
            tx["category"]["updated_at"].isoformat()
            if tx["category"]["updated_at"]
            else None
        )
        tx["user_currency"]["created_at"] = tx["user_currency"][
            "created_at"
        ].isoformat()
        tx["user_currency"]["updated_at"] = (
            tx["user_currency"]["updated_at"].isoformat()
            if tx["user_currency"]["updated_at"]
            else None
        )

        tx["user_currency"]["currency"]["created_at"] = tx["user_currency"]["currency"][
            "created_at"
        ].isoformat()
        tx["user_currency"]["currency"]["updated_at"] = (
            tx["user_currency"]["currency"]["updated_at"].isoformat()
            if tx["user_currency"]["currency"]["updated_at"]
            else None
        )
        tx["account"]["created_at"] = tx["account"]["created_at"].isoformat()
        tx["account"]["updated_at"] = (
            tx["account"]["updated_at"].isoformat()
            if tx["account"]["updated_at"]
            else None
        )

    def _fetch_and_prepare_transactions(
        self, category_id: int, user_id: int, session_id: str
    ) -> tuple[list[dict], Decimal]:
        """Fetch transactions and prepare them for caching."""
        transactions = self.crud_transaction.get_transaction_by_category_id(
            category_id=category_id, user_id=user_id
        )

        transactions = [convert_sql_models_to_dict(tx) for tx in transactions]

        for tx in transactions:
            self._serialize_transaction_dates(tx)
        total_transactions_amount = self._calculate_total_amount(transactions)

        full_payload = {
            "transactions": transactions,
            "total_amount_in_default": float(total_transactions_amount),
        }

        self.redis_client.set(
            f"ai_insight:transactions:{user_id}:{session_id}",
            json.dumps(full_payload, default=float),
            ex=3600,
        )

        return transactions, total_transactions_amount

    def _calculate_total_amount(self, transactions: list[dict]) -> Decimal:
        """Calculate the total transaction amount in default currency."""
        total_transactions_amount = Decimal(0)

        for trans in transactions:
            account_currency = trans["user_currency"]["exchange_rate"]
            amount = Decimal(trans["amount_in_default"])
            rate = Decimal(str(account_currency))

            trans["amount_in_default"] = (amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            total_transactions_amount += trans["amount_in_default"]
        print(f"Total transactions amount: {total_transactions_amount}")
        return total_transactions_amount

    def _get_currency_code(self, user_id: int) -> str:
        """Get the user's default currency code or fallback to USD."""
        default_currency = self.crud_user_currency.get_user_default_currency(user_id)
        currency_code = default_currency.currency.code if default_currency else None

        if not currency_code:
            currency_code = "USD"

        return currency_code

    def _build_insight_payload(
        self,
        rsp: NLResolveResult,
        query: str,
        total_amount: Decimal,
        currency_code: str,
    ) -> dict:
        """Build the final payload for insight query."""
        amount = from_minor_units(
            amount_minor=total_amount,
            currency=currency_code,
        )

        target_text = query
        if rsp.parse and rsp.parse.target_text:
            target_text = rsp.parse.target_text

        payload = {
            "category": (
                rsp.resolved_candidates[0].category
                if len(rsp.resolved_candidates) > 0
                else target_text
            ),
            "amount": float(amount),
            "currency": currency_code,
        }

        return payload

    async def get_messages(self, user_id: int):
        messages = self.crud_chat.get_messages_by_user_id(user_id=user_id)
        return messages

    async def get_message_history_for_ai_context(self, user_id: int, session_id: str):
        messages = self.crud_chat.get_messages_by_user_id_and_session_id(
            user_id=user_id, session_id=session_id
        )
        return messages

    async def get_last_query_plan(self, user_id: int, session_id: str):
        query_plan_json = self.redis_client.get(f"ai_insight:{user_id}:{session_id}")
        return query_plan_json if query_plan_json else "{}"

    async def get_transactions_for_insight(self, user_id: int, session_id: str):
        transactions_json = self.redis_client.get(
            f"ai_insight:transactions:{user_id}:{session_id}"
        )

        return transactions_json if transactions_json else "[]"

    async def save_message(
        self,
        user_id: int,
        content: str,
        role: ChatRoleEnum,
        session_id: str,
        llm_model: str,
    ):
        message_obj = ChatMessageCreate(
            user_id=user_id,
            content=content,
            role=role,
            session_id=session_id,
            llm_model=llm_model,
        )
        chat = self.crud_chat.create(message_obj)
        return chat
