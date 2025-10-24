from sqlalchemy import Column
from sqlalchemy.orm import joinedload
from crud.base import CRUDBase
from models.planner import Planner


class CRUDPlanner(CRUDBase[Planner]):
    def get_planner_by_user_id(self, user_id: Column[int]) -> list[Planner]:
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .options(
                joinedload(self.model.category), joinedload(self.model.user_currency)
            )
            .all()
        )

    def get_planner_by_id(self, id: int) -> Planner | None:
        return (
            self.db.query(self.model)
            .filter(self.model.id == id)
            .options(joinedload(Planner.category), joinedload(Planner.user_currency))
            .first()
        )


def get_crud_planner():
    return CRUDPlanner(Planner)
