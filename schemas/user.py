from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.category import UserCategoryResponse
from schemas.currency import UserCurrencyResponse
from schemas.subscription import UserSubscriptionResponse


class RegisterPayload(BaseModel):
    id_token: str
    name: str


class RegisterCreate(BaseModel):
    name: str
    email: str
    uid: str


class RegisterResponse(BaseModel):
    id: int
    uid: str
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    subscription: Optional[UserSubscriptionResponse] = None
    currencies: list[UserCurrencyResponse] = []
    categories: list[UserCategoryResponse] = []
