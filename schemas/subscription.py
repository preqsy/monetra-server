from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel

from schemas.base import ReturnBaseModel


class UserSubscriptionCreate(BaseModel):
    plan_id: int
    user_id: Optional[int] = None
    start_date: Optional[datetime] = datetime.now(timezone.utc)
    end_date: Optional[datetime] = None
    is_active: bool = True


class UserSubscriptionResponse(ReturnBaseModel, UserSubscriptionCreate):
    pass


class PlanFeatureResponse(ReturnBaseModel):
    feature_name: str
    description: str
    plan_id: int
    enabled: bool


class SubscriptionPlanResponse(ReturnBaseModel):
    id: int
    name: str
    price: int
    billing_cycle: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    features: List[PlanFeatureResponse] = []
