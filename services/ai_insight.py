from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4
from httpx import AsyncClient

from core.exceptions import InvalidRequest
from crud.chat import CRUDChat
from crud.currency import CRUDUserCurrency
from crud.transaction import CRUDTransaction
from schemas.ai_schemas import NLResolveResult
from schemas.chat import ChatMessageCreate
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
    ):
        self.http_client = AsyncClient(base_url=settings.AI_SERVICE_URL, timeout=60.0)
        self.crud_transaction = crud_transaction
        self.crud_user_currency = crud_user_currency
        self.crud_chat = crud_chat

    async def create_session(self, user_id: int):
        return str(user_id) + "-" + str(uuid4())

    async def query_insight(self, query: str, user_id: int):
        print("Querying AI Insight Service with query:", settings.AI_SERVICE_URL, query)

        chat_obj = ChatMessageCreate(
            user_id=user_id,
            role=ChatRoleEnum.USER,
            content=query,
        )
        response = await self.http_client.post(
            "/nl/resolve",
            json={"query": query, "user_id": user_id},
            headers={"monetra-ai-key": settings.BACKEND_HEADER},
            params={"llm_provider": "groq"},
        )
        # response.raise_for_status()
        rsp = NLResolveResult(**response.json())

        if not rsp.ok:
            raise InvalidRequest()

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
        print("Currency code:", currency_code)

        payload = {
            "category": (
                rsp.resolved_candidates[0].category
                if len(rsp.resolved_candidates) > 0
                else rsp.parse.target_text
            ),
            "amount": float((amount)),
            "currency": currency_code,
        }
        print("Total amount:", float(amount))

        async with self.http_client.stream(
            "POST",
            "nl/format",
            json=payload,
            headers={"monetra-ai-key": settings.BACKEND_HEADER},
            params={"llm_provider": "groq"},
        ) as rsp:
            rsp.raise_for_status()

            async for line in rsp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    # print("Sending line:", line)
                    yield line + " " + "\n\n"
