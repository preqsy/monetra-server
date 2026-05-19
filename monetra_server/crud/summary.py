from datetime import date
from core.db import get_db
from crud.base import CRUDBase
from models.views import TotalSummary


class CRUDTotalSummary(CRUDBase[TotalSummary]):
    def get_total_summary(self, user_id: int, date: date):
        query = (
            self.db.query(TotalSummary)
            .filter(TotalSummary.user_id == user_id, TotalSummary.month == date.month)
            .filter(TotalSummary.year == date.year)
            .first()
        )
        return query


db_session = next(get_db())


def get_crud_total_summary() -> CRUDTotalSummary:
    return CRUDTotalSummary(model=TotalSummary, db=db_session)
