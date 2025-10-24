from datetime import date
from fastapi import APIRouter, Depends

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_external_service
from models.user import User
from schemas.account import MonoAccountCreate
from services.external import ExternalService

router = APIRouter(prefix="", tags=["Plaid Mono"])


@router.post("/plaid/link-token")
async def plaid_create_link_token(
    user: User = Depends(get_current_user),
    external_service: ExternalService = Depends(get_external_service),
):
    result = await external_service.plaid_create_link_token(user)

    return result


@router.post("/plaid/exchange-token")
async def exchange_public_token(
    public_token: str,
    user: User = Depends(get_current_user),
    external_service: ExternalService = Depends(get_external_service),
):
    return await external_service.plaid_exchange_public_token(public_token)


@router.get("/plaid/transactions")
async def get_transactions(
    access_token: str,
    user: User = Depends(get_current_user),
    external_service: ExternalService = Depends(get_external_service),
):
    result = await external_service.get_transactions(access_token)

    return result


@router.post(
    "/mono/exchange-code",
    response_model=MonoAccountCreate,
)
async def exchange_code(
    code: str,
    start_date: date = None,
    user: User = Depends(get_current_user),
    external_service: ExternalService = Depends(get_external_service),
):

    return await external_service.mono_exchange_code(
        code=code,
        user=user,
        transaction_start_date=start_date,
    )
