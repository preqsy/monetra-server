from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import ClassVar, Optional

from schemas.base import ReturnBaseModel
from schemas.currency import UserCurrencyResponse
from schemas.enums import (
    AccountCategoryEnum,
    AccountMethodEnum,
    AccountProviderEnum,
    AccountTypeEnum,
)


class AccountBase(BaseModel):
    name: str
    user_currency_id: int = 1
    amount: int
    account_type: AccountTypeEnum  # AUTOMATIC(MONO), MANUAL
    account_category: AccountCategoryEnum  # CREDIT, BALANCE
    notes: Optional[str] = None
    amount_base: Optional[int] = 0


class AccountCreate(AccountBase):
    IS_DELETED: ClassVar[str] = "is_deleted"
    user_id: Optional[int] = None
    credit_amount: int = 0  # TODO: Remove this
    account_type: AccountTypeEnum = AccountTypeEnum.MANUAL  # AUTOMATIC(MONO), MANUAL
    account_category: AccountCategoryEnum = (
        AccountCategoryEnum.BALANCE
    )  # CREDIT, BALANCE
    account_method: Optional[AccountMethodEnum] = (
        None  # e.g., CASH, VISA, MASTERCARD, CRYPTO
    )


class MonoAccountCreate(AccountBase):
    LAST_SYNC_DATE: ClassVar[str] = "last_sync_date"
    user_id: int
    account_type: AccountTypeEnum = AccountTypeEnum.AUTOMATIC
    account_category: AccountCategoryEnum = AccountCategoryEnum.BALANCE
    account_number: Optional[str] = None
    ext_account_id: str
    account_provider: AccountProviderEnum = AccountProviderEnum.MONO
    last_sync_date: Optional[datetime] = None


class PlaidAccountCreate(AccountBase):
    user_id: int
    access_token: str
    account_type: AccountTypeEnum = AccountTypeEnum.AUTOMATIC
    account_category: AccountCategoryEnum = AccountCategoryEnum.BALANCE
    account_number: Optional[str] = None
    ext_account_id: str
    account_provider: AccountProviderEnum = AccountProviderEnum.PLAID


class AccountResponse(ReturnBaseModel, AccountBase):
    user_id: int
    account_method: Optional[AccountMethodEnum] = None


class FullAccountResponse(ReturnBaseModel, AccountBase):
    user_id: int
    last_sync_date: Optional[datetime] = None
    user_currency: UserCurrencyResponse


class AccountWithBalanceResponse(BaseModel):
    total_balance: Decimal = Decimal(0)
    accounts: list[FullAccountResponse]


class MonoInstitution(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    bank_code: Optional[str] = None
    type: Optional[str] = None


class MonoCustomer(BaseModel):
    id: str


class MonoAccount(BaseModel):
    id: str
    name: str
    currency: str
    balance: int
    type: str
    account_number: str
    institution: Optional[MonoInstitution] = None


class MonoAccountResponse(BaseModel):
    account: MonoAccount
    customer: MonoCustomer
