from datetime import date
from fastapi import APIRouter, Depends, Query, status

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_transaction_service
from models.user import User
from schemas.transaction import TransactionCreate, TransactionResponse
from services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction_data: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    return await transaction_service.create_transaction(transaction_data, user.id)


@router.get(
    "",
    response_model=list[TransactionResponse],
)
async def get_user_transactions(
    date: date = Query(
        date.today(), description="Date to filter the summary by (YYYY-MM-DD)"
    ),
    transaction_service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    return await transaction_service.list_user_transactions(user.id, date)


@router.get(
    "/account/{account_id}",
    response_model=list[TransactionResponse],
)
async def get_transactions_by_account(
    account_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    return await transaction_service.get_account_transactions(account_id, user.id)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
async def get_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    return await transaction_service.get_single_transaction(transaction_id, user.id)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    await transaction_service.delete_transaction(transaction_id, user.id)
