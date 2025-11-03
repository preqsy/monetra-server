from typing import Optional
from sqlalchemy.orm import joinedload

from crud.base import CRUDBase
from models.budget import Budget

from schemas.enums import BudgetPeriodEnum, BudgetTypeEnum


class CRUDBudget(CRUDBase[Budget]):
    def get_budgets_by_user_id(self, user_id: int) -> list[Budget]:
        return self.db.query(Budget).filter(Budget.user_id == user_id).all()

    def get_budget_by_period(
        self,
        user_id: int,
        period: BudgetPeriodEnum,
        type: Optional[BudgetTypeEnum] = None,
    ) -> list[Budget] | Optional[Budget]:
        query = self.db.query(Budget).filter(
            Budget.user_id == user_id, Budget.period == period
        )
        if type:
            query = query.filter(Budget.type == type)
            return query.one_or_none()
        return query.options(
            joinedload(Budget.user_currency), joinedload(Budget.category)
        ).all()

    def get_total_budget(self, user_id: int, period: BudgetPeriodEnum) -> list[Budget]:
        return (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.period == period,
            )
            .all()
        )


def get_crud_budget() -> CRUDBudget:
    return CRUDBudget(model=Budget)
