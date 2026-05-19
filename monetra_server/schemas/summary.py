from typing import Optional
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    user_id: int
    total_income: float
    total_expense: float
    net_total: float
    total_cash_at_hand: float
    total_balance: float
    default_user_currency_id: Optional[int] = None
    default_currency_code: Optional[str] = None
    month: int
    year: int
