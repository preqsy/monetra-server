from httpx import AsyncClient

from core import settings
from core.exceptions import InvalidRequest


class ExchangeRateClient:
    def __init__(self):
        self.client = AsyncClient(base_url=settings.EXCHANGE_RATE_BASE_URL)
        self.api_key = settings.EXCHANGE_API_KEY

    async def get_exchange_rate(self, target_currency_code: str) -> dict:
        response = await self.client.get(
            f"/{self.api_key}/latest/{target_currency_code}",
        )
        if response.status_code != 200:
            raise InvalidRequest(message="Failed to retrieve exchange rate")
        data = response.json()
        return data["conversion_rates"]


def get_exchange_rate(target_currency_code: str):
    return ExchangeRateClient().get_exchange_rate(
        target_currency_code=target_currency_code
    )
