from datetime import date
from crud.summary import CRUDTotalSummary


class AccountSummaryService:
    def __init__(
        self,
        crud_total_summary: CRUDTotalSummary,
    ):
        self.crud_total_summary = crud_total_summary

    def get_account_summary(self, user_id: int, date: date):
        print(
            f"Getting summary for user_id: {user_id} and date: {date.month}-{date.year}"
        )
        summary = self.crud_total_summary.get_total_summary(user_id=user_id, date=date)
        if not summary:
            return {
                "user_id": user_id,
                "total_income": 0.0,
                "total_expense": 0.0,
                "net_total": 0.0,
                "total_cash_at_hand": 0.0,
                "total_balance": 0.0,
                "default_user_currency_id": None,
                "default_currency_code": None,
                "month": date.month,
                "year": date.year,
            }
        return summary
