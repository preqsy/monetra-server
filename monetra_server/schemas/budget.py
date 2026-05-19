from typing import Optional
from pydantic import BaseModel

from schemas.base import ReturnBaseModel
from schemas.enums import BudgetPeriodEnum, BudgetTypeEnum
from schemas.currency import UserCurrencyResponse
from schemas.category import CreateCategoryResponse


class BudgetCreate(BaseModel):
    name: Optional[str] = None
    amount: int
    # amount_in_default: Optional[int] = None
    category_id: int
    user_currency_id: Optional[int] = None
    user_id: Optional[int] = None
    period: BudgetPeriodEnum
    type: BudgetTypeEnum


class TotalBudgetCreate(BaseModel):
    amount: int
    period: BudgetPeriodEnum
    user_currency_id: Optional[int] = None


class BudgetResponse(ReturnBaseModel, BudgetCreate):
    user_currency: UserCurrencyResponse
    category: Optional[CreateCategoryResponse] = None


class BudgetWithAmountResponse(BudgetResponse):
    spent_amount: Optional[int] = 0


class TotalBudgetResponse(BaseModel):
    total_budget: int
    total_spent: int
