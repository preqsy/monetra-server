from datetime import date
from crud.summary import CRUDTotalSummary
from services.account import AccountService
from services.transaction import TransactionService


class AccountSummaryService:
    def __init__(
        self,
        crud_total_summary: CRUDTotalSummary,
        account_service: AccountService,
        transaction_service: TransactionService,
    ):
        self.crud_total_summary = crud_total_summary
        self.account_service = account_service
        self.transaction_service = transaction_service

    async def get_account_summary(self, user_id: int, date: date):
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
        # summary = await self.calculate_account_balance(user_id=user_id)

        net_total = await self.get_total_income_and_expenses(user_id=user_id)

        print(f"Summary fetched: {net_total}")
        return summary

    async def get_account_balance(self, user_id: int):
        return await self.account_service.calculate_account_balance(user_id=user_id)

    async def get_total_income_and_expenses(self, user_id: int):
        return await self.transaction_service.calculate_total_income_and_expenses(
            user_id=user_id
        )
