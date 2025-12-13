from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pprint import pprint
from crud.account import CRUDAccount
from crud.summary import CRUDTotalSummary
from utils.helper import convert_sql_models_to_dict
import time


class AccountSummaryService:
    def __init__(
        self,
        crud_total_summary: CRUDTotalSummary,
        crud_account: CRUDAccount,
    ):
        self.crud_total_summary = crud_total_summary
        self.crud_account = crud_account

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
        return summary

    async def calculate_account_balance(self, user_id: int):
        accounts = self.crud_account.get_public_accounts(user_id=user_id)

        accounts = [convert_sql_models_to_dict(account) for account in accounts]
        total_balance = Decimal(0)

        for account in accounts:
            exchange_rate = Decimal(account["user_currency"]["exchange_rate"])
            amount = Decimal(account["amount"])
            account["amount_in_default"] = (amount / exchange_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            total_balance += account["amount_in_default"]

        return total_balance

    async def get_total_income_and_expenses(self, user_id: int): ...
