from datetime import date
from httpx import AsyncClient

from dateutil.relativedelta import relativedelta
from core import settings
from core.exceptions import InvalidRequest
from core.externals.schema import MonoTransactionSchema
from schemas.account import MonoAccountResponse


class MonoClient:
    def __init__(self):
        self.client = AsyncClient(base_url=settings.MONO_BASE_URL)
        self.header = {"mono-sec-key": settings.MONO_SECRET_KEY}

    async def exchange_code(self, code: str):
        rsp = await self.client.post(
            url="/accounts/auth",
            headers=self.header,
            json={"code": code},
        )
        if rsp.status_code != 200:
            raise InvalidRequest(
                message=rsp.json().get("message", "Failed to exchange code")
            )
        return rsp.json()

    async def get_account(self, account_id: str):
        rsp = await self.client.get(
            url=f"/accounts/{account_id}",
            headers=self.header,
        )
        if rsp.status_code != 200:
            raise InvalidRequest(
                message=rsp.json().get("message", "Failed to retrieve account")
            )
        # print(f"Return data: {rsp.json()}")
        return MonoAccountResponse(**rsp.json().get("data", {}))

    async def get_transactions(
        self,
        account_id: str,
        start_date: date = None,
        end_date: date = date.today(),
    ):
        if not start_date:
            start_date = date.today() - relativedelta(months=1)
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")

        rsp = await self.client.get(
            url=f"/accounts/{account_id}/transactions?start_date={start_str}&end_date={end_str}",
            headers={"mono-sec-key": settings.MONO_SECRET_KEY},
        )
        if rsp.status_code != 200:
            raise InvalidRequest(
                message=rsp.json().get("message", "Failed to retrieve transactions")
            )
        return [MonoTransactionSchema(**tx) for tx in rsp.json().get("data", {})]


def get_mono_client() -> MonoClient:
    return MonoClient()
