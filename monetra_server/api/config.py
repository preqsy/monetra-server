from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.externals.exchange_rate.exchangerate_api import (
    get_exchange_rate,
)

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("/exchange-rates/{currency_code}")
async def get_exchange_rates(
    currency_code: str,
):
    return await get_exchange_rate(currency_code)


@router.get("/health")
async def health_check():
    return JSONResponse(content={"message": "Monetra server is healthy"})
