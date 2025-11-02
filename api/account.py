from fastapi import APIRouter, Depends

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_account_service
from models.user import User
from schemas.account import AccountCreate, AccountResponse, AccountWithBalanceResponse
from services import AccountService

router = APIRouter(prefix="/accounts", tags=["Account"])


@router.post("", response_model=AccountResponse)
async def create_account(
    data_obj: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return await account_service.create_account(data_obj=data_obj, user_id=user.id)


@router.get(
    "",
    response_model=AccountWithBalanceResponse,
)
async def list_accounts(
    account_service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return await account_service.list_accounts(user_id=user.id)


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data_obj: AccountCreate,  # TODO: UPDATE THE SCHEMA
    account_service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return await account_service.update_account(
        account_id=account_id, data_obj=data_obj, user_id=user.id
    )


@router.delete("/{account_id}", response_model=AccountResponse)
async def delete_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return await account_service.delete_account(account_id=account_id, user_id=user.id)
