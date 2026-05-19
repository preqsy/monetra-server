from sqlalchemy import Column
from sqlalchemy.orm import joinedload
from core.db import get_db
from crud.base import CRUDBase
from models.currency import UserCurrency
from models.planner import Planner


class CRUDPlanner(CRUDBase[Planner]):
    def get_planner_by_user_id(self, user_id: Column[int]) -> list[Planner]:
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .options(
                joinedload(self.model.category),
                joinedload(self.model.user_currency).joinedload(UserCurrency.currency),
            )
            .all()
        )

    def get_planner_by_id(self, id: int) -> Planner | None:
        return (
            self.db.query(self.model)
            .filter(self.model.id == id)
            .options(
                joinedload(Planner.category),
                joinedload(Planner.user_currency).joinedload(UserCurrency.currency),
            )
            .first()
        )


db_session = next(get_db())


def get_crud_planner():
    return CRUDPlanner(model=Planner, db=db_session)
