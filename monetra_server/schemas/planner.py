from datetime import date
from decimal import Decimal
from pydantic import AnyHttpUrl, BaseModel, Field
from typing import ClassVar, Optional

from schemas.base import ReturnBaseModel
from schemas.category import CreateCategoryResponse
from schemas.currency import UserCurrencyResponse
from schemas.enums import PlannerRoleEnum, PlannerTypeEnum
from schemas.transaction import TransactionResponse


class PlannerBase(BaseModel):
    type: PlannerTypeEnum
    name: str
    required_amount: int
    accumulated_amount: int
    date: date
    required_amount_in_default: Optional[int] = 0
    accumulated_amount_in_default: Optional[int] = 0
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    user_currency_id: Optional[int] = None
    role: Optional[PlannerRoleEnum] = None
    note: Optional[str] = None
    image: Optional[AnyHttpUrl] = None
    account_id: Optional[int] = None


class PlannerCreate(PlannerBase):
    pass


class PlannerUpdate(BaseModel):
    NAME: ClassVar[str] = "name"
    REQUIRED_AMOUNT: ClassVar[str] = "required_amount"

    name: Optional[str] = None
    required_amount: Optional[int] = Field(gt=0, default=0)
    required_amount_in_default: Optional[int] = Field(default=0, gt=0)
    role: Optional[str] = None
    note: Optional[str] = None
    date: Optional[date] = None
    image: Optional[str] = None


class PlannerAmountUpdate(BaseModel):
    accumulated_amount: int
    accumulated_amount_in_default: Optional[int] = Field(default=0)
    account_id: Optional[int] = None
    user_currency_id: Optional[int] = None


class PlannerCreateResponse(ReturnBaseModel, PlannerBase):
    pass


class PlannerResponse(ReturnBaseModel, PlannerBase):
    required_amount_in_default: Decimal = Decimal("0.00")
    accumulated_amount_in_default: Decimal = Decimal("0.00")
    category: CreateCategoryResponse
    user_currency: UserCurrencyResponse


class PlannerWithTransactionsResponse(PlannerResponse):
    transactions: list[TransactionResponse] = []
