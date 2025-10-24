import httpx
from datetime import datetime, timedelta
from core.config import settings
from core.exceptions import InvalidRequest
from core.externals.schema import (
    PlaidAccountResponse,
    PlaidExchangeTokenResponse,
    PlaidRequestTokenResponse,
)


class PlaidClient:
    def __init__(self):
        self.env = settings.PLAID_ENV
        self.base_url = self._get_base_url()
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self.client_id = settings.PLAID_CLIENT_ID
        self.secret = settings.PLAID_SECRET

    def _get_base_url(self):
        env_map = {
            "sandbox": settings.PLAID_BASE_URL_SANDBOX,
            "development": settings.PLAID_BASE_URL_DEVELOPMENT,
            "production": settings.PLAID_BASE_URL_PRODUCTION,
        }
        return env_map.get(self.env, env_map["sandbox"])

    async def create_link_token(self, user_id: int):
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "user": {"client_user_id": str(user_id)},
            "client_name": "FinFlow",
            "products": ["transactions"],
            "country_codes": ["US"],
            "language": "en",
        }
        rsp = await self.client.post("/link/token/create", json=payload)
        if rsp.status_code != 200 and rsp.status_code != 201:
            raise InvalidRequest(message=f"Failed to create link token")
        return PlaidRequestTokenResponse(**rsp.json())

    async def exchange_public_token(self, public_token: str):
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "public_token": public_token,
        }

        rsp = await self.client.post("/item/public_token/exchange", json=payload)
        if rsp.status_code != 200 and rsp.status_code != 201:
            raise InvalidRequest(message="Failed to exchange public token")
        return PlaidExchangeTokenResponse(**rsp.json())

    async def get_accounts(self, access_token: str):
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": access_token,
        }
        rsp = await self.client.post("/auth/get", json=payload)
        if rsp.status_code != 200 and rsp.status_code != 201:
            raise InvalidRequest(message="Failed to exchange public token")
        return PlaidAccountResponse(**rsp.json())

    async def fetch_transactions(self, access_token: str):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        payload = {
            "client_id": self.client_id,
            "secret": self.secret,
            "access_token": access_token,
            "start_date": str(start_date),
            "end_date": str(end_date),
        }
        rsp = await self.client.post("/transactions/get", json=payload)
        if rsp.status_code != 200 and rsp.status_code != 201:
            raise InvalidRequest(message="Failed to fetch transactions")
        return rsp.json()


def get_plaid_client() -> PlaidClient:
    return PlaidClient()
