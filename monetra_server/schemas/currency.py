from typing import Optional
from pydantic import BaseModel
from decimal import Decimal

from schemas.base import ReturnBaseModel


class UserCurrencyCreate(BaseModel):
    user_id: Optional[int] = None
    currency_id: int
    exchange_rate: Decimal
    is_default: bool = False


class CurrencyResponse(BaseModel):
    code: str
    name: str
    id: int
    symbol: Optional[str] = None


class UserCurrencyResponse(ReturnBaseModel, UserCurrencyCreate):
    currency: CurrencyResponse


class UserCurrencyUpdate(BaseModel):
    id: Optional[int] = None
    exchange_rate: Optional[Decimal] = None
    is_default: Optional[bool] = None
