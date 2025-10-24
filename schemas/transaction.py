from decimal import Decimal
from pydantic import AnyHttpUrl, BaseModel
from typing import Optional
from datetime import datetime

from schemas.account import AccountResponse
from schemas.base import ReturnBaseModel
from schemas.category import CreateCategoryResponse
from schemas.currency import UserCurrencyResponse
from schemas.enums import TransactionTypeEnum


class TransactionBase(BaseModel):
    user_id: Optional[int] = None
    amount: int = 0
    transaction_type: TransactionTypeEnum
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    user_currency_id: Optional[int] = None
    date: Optional[datetime] = None
    amount_in_default: Optional[int] = 0


class TransactionCreate(TransactionBase):
    is_paid: bool = True
    notes: Optional[str] = None
    repeat: Optional[str] = None
    remind: Optional[str] = None
    image: Optional[AnyHttpUrl] = None


class TransactionResponse(ReturnBaseModel, TransactionCreate):
    amount_in_default: Decimal = Decimal("0.00")
    account: AccountResponse
    user_currency: UserCurrencyResponse
    category: CreateCategoryResponse


class MonoTransactionCreate(TransactionBase):
    mono_transaction_id: str
    mono_type: Optional[str] = None
    narration: Optional[str] = None
    balance: Optional[int] = 0
