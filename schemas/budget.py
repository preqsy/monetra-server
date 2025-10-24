from typing import Optional
from pydantic import BaseModel

from schemas.base import ReturnBaseModel
from schemas.enums import BudgetPeriodEnum, BudgetTypeEnum


class BudgetCreate(BaseModel):
    name: Optional[str] = None
    amount: int
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
    pass


class BudgetWithAmountResponse(ReturnBaseModel, BudgetCreate):
    spent_amount: Optional[int] = 0


class TotalBudgetResponse(BaseModel):
    total_budget: int
    total_spent: int
