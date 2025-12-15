from typing import Optional
from sqlalchemy.orm import joinedload
from core.db import get_db
from crud.base import CRUDBase
from models.user import SubscriptionPlan, UserSubscription


class CRUDUserSubscription(CRUDBase[UserSubscription]):
    def get_by_user_id(self, *, user_id: int) -> Optional[UserSubscription]:
        return (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user_id)
            .first()
        )


class CRUDSubscriptionPlan(CRUDBase[SubscriptionPlan]):
    def get_subscription_by_id(self, *, plan_id: int) -> Optional[SubscriptionPlan]:
        return (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.id == plan_id)
            .first()
        )

    def get_subscriptions(self) -> list[SubscriptionPlan]:
        return (
            self.db.query(SubscriptionPlan)
            .options(joinedload(SubscriptionPlan.features))
            .all()
        )


db_session = next(get_db())


def get_crud_user_subscription() -> CRUDUserSubscription:
    return CRUDUserSubscription(model=UserSubscription, db=db_session)


def get_crud_subscription_plan() -> CRUDSubscriptionPlan:
    return CRUDSubscriptionPlan(model=SubscriptionPlan, db=db_session)
