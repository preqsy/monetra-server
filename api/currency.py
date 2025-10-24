from fastapi import APIRouter, Depends

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_currency_service
from models.user import User
from schemas.currency import (
    CurrencyResponse,
    UserCurrencyCreate,
    UserCurrencyResponse,
    UserCurrencyUpdate,
)
from services import CurrencyService


router = APIRouter(prefix="/currencies", tags=["Currency"])


@router.post(
    "",
    response_model=UserCurrencyCreate,
)
async def add_currency(
    data_obj: UserCurrencyCreate,
    currency_service: CurrencyService = Depends(get_currency_service),
    user: User = Depends(get_current_user),
):
    return await currency_service.add_currency(data_obj=data_obj, user_id=user.id)


@router.get(
    "",
    response_model=list[CurrencyResponse],
)
async def list_currencies(
    currency_service: CurrencyService = Depends(get_currency_service),
    # user: User = Depends(get_current_user),
):
    return currency_service.crud_currency.get_all_currencies()


@router.get(
    "/user",
    response_model=list[UserCurrencyResponse],
)
async def get_user_currencies(
    currency_service: CurrencyService = Depends(get_currency_service),
    user: User = Depends(get_current_user),
):
    return currency_service.crud_user_currency.get_user_currencies(user_id=user.id)


@router.put(
    "",
)
async def update_default_currency(
    data_obj: UserCurrencyUpdate,
    account_service: CurrencyService = Depends(get_currency_service),
    user: User = Depends(get_current_user),
):
    return await account_service.update_default_currency(
        user_id=user.id, data_obj=data_obj
    )
