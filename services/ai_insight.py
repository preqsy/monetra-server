from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4
from httpx import AsyncClient, HTTPError

import logfire

from core.exceptions import InvalidRequest, MissingResource
from crud.chat import CRUDChat, CRUDSession
from crud.currency import CRUDUserCurrency
from crud.transaction import CRUDTransaction
from schemas.ai_schemas import NLResolveResult
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
    ):
        self.http_client = AsyncClient(base_url=settings.AI_SERVICE_URL, timeout=600.0)
        self.crud_transaction = crud_transaction
        self.crud_user_currency = crud_user_currency
        self.crud_chat = crud_chat
        self.crud_session = crud_session

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

    async def prepare_insight(self, query: str, user_id: int, session_id: str) -> dict:

        logfire.info(f"Using: {settings.LLM_PROVIDER} from the backend")

        if not self.crud_session.get_session_by_session_id(
            session_id=session_id, user_id=user_id
        ):
            logfire.warning(
                f"Session ID not found for user_id: {user_id} with session_id: {session_id}"
            )
            raise MissingResource(message="Session ID not found")

        # Save user message
        chat_obj = ChatMessageCreate(
            user_id=user_id,
            role=ChatRoleEnum.USER,
            content=query,
            session_id=session_id,
        )
        self.crud_chat.create(chat_obj)

        # Call NL resolve endpoint
        response = await self.http_client.post(
            "/nl/resolve",
            json={"query": query, "user_id": user_id},
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

        transactions = self.crud_transaction.get_transaction_by_category_id(
            category_id=rsp.resolved_category_id, user_id=user_id
        )

        transactions = [convert_sql_models_to_dict(tx) for tx in transactions]
        total_transactions_amount = 0

        for trans in transactions:
            account_currency = trans["user_currency"]["exchange_rate"]
            amount = Decimal(trans["amount_in_default"])
            rate = Decimal(str(account_currency))

            trans["amount_in_default"] = (amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            total_transactions_amount += trans["amount_in_default"]

        default_currency = self.crud_user_currency.get_user_default_currency(user_id)
        currency_code = default_currency.currency.code if default_currency else None

        if not currency_code:
            currency_code = "USD"

        amount = from_minor_units(
            amount_minor=total_transactions_amount,
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
            "amount": float((amount)),
            "currency": currency_code,
        }
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

                ai_chat_obj = ChatMessageCreate(
                    user_id=user_id,
                    role=ChatRoleEnum.ASSISTANT,
                    content=text,
                    session_id=session_id,
                    llm_model=settings.LLM_PROVIDER,
                )
                self.crud_chat.create(ai_chat_obj)
        except HTTPError:
            yield "data: Unable to format insight response.\n\n"

    async def get_messages(self, user_id: int):
        messages = self.crud_chat.get_messages_by_user_id(user_id=user_id)
        return messages
