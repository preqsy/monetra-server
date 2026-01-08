from decimal import ROUND_HALF_UP, Decimal
from httpx import AsyncClient

from crud.transaction import CRUDTransaction
from schemas.ai_schemas import NLResolveResult
from utils.helper import convert_sql_models_to_dict


class AIInsightService:
    def __init__(
        self,
        crud_transaction: CRUDTransaction,
    ):
        self.http_client = AsyncClient(base_url="http://localhost:9000")
        self.crud_transaction = crud_transaction

    async def query_insight(self, query: str, user_id: int) -> Decimal:
        response = await self.http_client.post(
            "/nl/resolve",
            json={"query": query, "user_id": user_id},
            timeout=30.0,
        )
        # response.raise_for_status()
        rsp = NLResolveResult(**response.json())

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
        return total_transactions_amount
