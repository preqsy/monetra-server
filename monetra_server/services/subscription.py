from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from core.exceptions import InvalidRequest
from crud.subscription import CRUDSubscriptionPlan, CRUDUserSubscription
from schemas.enums import SubscriptionBillingCycleEnum
from schemas.subscription import UserSubscriptionCreate


class SubscriptionService:
    def __init__(
        self,
        crud_user_subscription: CRUDUserSubscription,
        crud_subscription_plan: CRUDSubscriptionPlan,
    ):
        self.crud_user_subscription = crud_user_subscription
        self.crud_subscription_plan = crud_subscription_plan

    async def list_subscription_plans(self):
        return self.crud_subscription_plan.get_subscriptions()

    async def create_subscription(
        self,
        *,
        user_id: int,
        data_obj: UserSubscriptionCreate,
    ):
        subscription_plan = self.crud_subscription_plan.get_subscription_by_id(
            plan_id=data_obj.plan_id
        )
        if not subscription_plan:
            raise InvalidRequest("Invalid subscription plan ID")

        data_obj.start_date = datetime.now(timezone.utc)
        if subscription_plan.billing_cycle == SubscriptionBillingCycleEnum.MONTHLY:
            end_date = data_obj.start_date + relativedelta(months=1)
        elif subscription_plan.billing_cycle == SubscriptionBillingCycleEnum.YEARLY:
            end_date = data_obj.start_date + relativedelta(years=1)
        elif subscription_plan.billing_cycle == SubscriptionBillingCycleEnum.LIFETIME:
            end_date = data_obj.start_date + relativedelta(years=100)
        else:
            raise InvalidRequest("Invalid billing cycle in subscription plan")
        data_obj.end_date = end_date
        data_obj.user_id = user_id
        subscription = self.crud_user_subscription.create(data_obj=data_obj)

        return subscription
