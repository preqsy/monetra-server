from fastapi import APIRouter, Depends, status

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_subscription_service
from models.user import User
from schemas.subscription import (
    SubscriptionPlanResponse,
    UserSubscriptionCreate,
    UserSubscriptionResponse,
)
from services.subscription import SubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[SubscriptionPlanResponse],
)
async def list_subscriptions(
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    return await subscription_service.list_subscription_plans()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSubscriptionResponse,
)
async def create_subscription(
    data_obj: UserSubscriptionCreate,
    user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    return await subscription_service.create_subscription(
        user_id=user.id, data_obj=data_obj
    )
