from datetime import date
from decimal import Decimal
from typing import Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from crud.transaction import CRUDTransaction
from crud.account import CRUDAccount
from crud.category import CRUDCategory, CRUDUserCategory
from crud.currency import CRUDUserCurrency
from crud.summary import CRUDTotalSummary
from crud.planner import CRUDPlanner
from models.account import Account
from models.transaction import Transaction
from services.transaction import TransactionService
from services.account import AccountService
from services.summary import AccountSummaryService
from utils.currency_conversion import from_minor_units


class TransactionQueryInput(BaseModel):
    user_id: int = Field(description="User ID to query transactions for")
    start_date: date | None = Field(
        default=None, description="Start date for transaction query (YYYY-MM-DD)"
    )
    end_date: date | None = Field(
        default=None, description="End date for transaction query (YYYY-MM-DD)"
    )
    category_id: int | None = Field(
        default=None, description="Category ID to filter by"
    )
    account_id: int | None = Field(default=None, description="Account ID to filter by")
    transaction_type: str | None = Field(
        default=None, description="Transaction type: 'income' or 'expense'"
    )
    limit: int | None = Field(
        default=50, description="Maximum number of transactions to return"
    )


class AccountQueryInput(BaseModel):
    user_id: int = Field(description="User ID to query accounts for")
    account_type: str | None = Field(default=None, description="Account type filter")
    account_category: str | None = Field(
        default=None, description="Account category filter"
    )


class SummaryQueryInput(BaseModel):
    user_id: int = Field(description="User ID to get summary for")
    summary_date: date | None = Field(
        default=None, description="Date for summary (defaults to current month)"
    )


class CategoryQueryInput(BaseModel):
    user_id: int = Field(description="User ID to query categories for")
    category_type: str | None = Field(
        default=None, description="Category type: 'income' or 'expenses'"
    )


class FinancialTools:
    """Collection of tools for querying financial data"""

    def __init__(
        self,
        crud_transaction: CRUDTransaction,
        crud_account: CRUDAccount,
        crud_category: CRUDCategory,
        crud_user_category: CRUDUserCategory,
        crud_user_currency: CRUDUserCurrency,
        crud_total_summary: CRUDTotalSummary,
        crud_planner: CRUDPlanner,
        transaction_service: TransactionService,
        account_service: AccountService,
        summary_service: AccountSummaryService,
    ):
        self.crud_transaction = crud_transaction
        self.crud_account = crud_account
        self.crud_category = crud_category
        self.crud_user_category = crud_user_category
        self.crud_user_currency = crud_user_currency
        self.crud_total_summary = crud_total_summary
        self.crud_planner = crud_planner
        self.transaction_service = transaction_service
        self.account_service = account_service
        self.summary_service = summary_service

    def get_transactions_tool(self) -> BaseTool:
        """Tool for querying user transactions"""
        financial_tools = self

        class TransactionQueryTool(BaseTool):
            name: str = "get_transactions"
            description: str = """
            Query user transactions with various filters. Use this to get
            transaction data for analysis. Can filter by date range, category,
            account, transaction type, and limit results.
            """
            args_schema: type[BaseModel] = TransactionQueryInput

            def _run(self, **kwargs) -> str:
                try:
                    user_id: int = kwargs["user_id"]
                    start_date = kwargs.get("start_date")
                    end_date = kwargs.get("end_date")
                    category_id = kwargs.get("category_id")
                    account_id = kwargs.get("account_id")
                    transaction_type = kwargs.get("transaction_type")
                    limit = kwargs.get("limit", 50)

                    # Get user transactions
                    transactions = (
                        financial_tools.crud_transaction.get_user_transactions_by_id(
                            user_id
                        )
                    )

                    # Apply filters
                    filtered_transactions: list[Transaction] = []
                    for transaction in transactions:
                        # Date filter
                        if start_date and transaction.date.date() < start_date:
                            continue
                        if end_date and transaction.date.date() > end_date:
                            continue

                        # Category filter
                        if category_id and transaction.category_id != category_id:
                            continue

                        # Account filter
                        if account_id and transaction.account_id != account_id:
                            continue

                        # Transaction type filter
                        if (
                            transaction_type
                            and transaction.transaction_type != transaction_type
                        ):
                            continue

                        filtered_transactions.append(transaction)

                    # Limit results
                    filtered_transactions = filtered_transactions[:limit]

                    # Format response
                    result = []
                    for transaction in filtered_transactions:
                        # Get currency info
                        user_currency = financial_tools.crud_user_currency.get(
                            int(transaction.user_currency_id)
                        )
                        currency_code = "USD"  # Default fallback
                        if (
                            user_currency
                            and hasattr(user_currency, "currency")
                            and user_currency.currency
                        ):
                            currency_code = getattr(
                                user_currency.currency, "code", "USD"
                            )

                        # Convert amount from minor units
                        amount = from_minor_units(
                            Decimal(transaction.amount), currency_code
                        )

                        result.append(
                            {
                                "id": transaction.id,
                                "narration": transaction.narration,
                                "amount": amount,
                                "currency": currency_code,
                                "transaction_type": transaction.transaction_type,
                                "category_id": transaction.category_id,
                                "account_id": transaction.account_id,
                                "date": transaction.date.isoformat(),
                                "is_paid": transaction.is_paid,
                                "notes": transaction.notes,
                            }
                        )

                    return f"Found {len(result)} transactions: {result}"

                except Exception as e:
                    return f"Error querying transactions: {str(e)}"

        return TransactionQueryTool()

    def get_accounts_tool(self) -> BaseTool:
        """Tool for querying user accounts"""
        financial_tools = self

        class AccountQueryTool(BaseTool):
            name: str = "get_accounts"
            description: str = """
            Query user accounts with optional filters. Use this to get account
            information and balances.
            """
            args_schema: type[BaseModel] = AccountQueryInput

            def _run(self, **kwargs) -> str:
                try:
                    user_id: int = kwargs["user_id"]
                    account_type = kwargs.get("account_type")
                    account_category = kwargs.get("account_category")

                    # Get user accounts
                    accounts = financial_tools.crud_account.get_public_accounts(user_id)

                    # Apply filters
                    filtered_accounts: list[Account] = []
                    for account in accounts:
                        if account_type and account.account_type != account_type:
                            continue
                        if (
                            account_category
                            and account.account_category != account_category
                        ):
                            continue

                        filtered_accounts.append(account)

                    # Format response
                    result = []
                    for account in filtered_accounts:
                        # Get currency info
                        user_currency = financial_tools.crud_user_currency.get(
                            int(account.user_currency_id)
                        )
                        currency_code = "USD"  # Default fallback
                        if (
                            user_currency
                            and hasattr(user_currency, "currency")
                            and user_currency.currency
                        ):
                            currency_code = getattr(
                                user_currency.currency, "code", "USD"
                            )

                        # Convert amount from minor units
                        amount = from_minor_units(
                            Decimal(str(account.amount or 0)), currency_code
                        )

                        result.append(
                            {
                                "id": account.id,
                                "name": account.name,
                                "amount": amount,
                                "currency": currency_code,
                                "account_type": account.account_type,
                                "account_category": account.account_category,
                                "account_provider": account.account_provider,
                                "notes": account.notes,
                            }
                        )

                    return f"Found {len(result)} accounts: {result}"

                except Exception as e:
                    return f"Error querying accounts: {str(e)}"

        return AccountQueryTool()

    def get_summary_tool(self) -> BaseTool:
        """Tool for getting financial summary"""
        financial_tools = self

        class SummaryQueryTool(BaseTool):
            name: str = "get_financial_summary"
            description: str = """
            Get financial summary for a user including total income, expenses,
            and net amount for a specific month.
            """
            args_schema: type[BaseModel] = SummaryQueryInput

            def _run(self, **kwargs) -> str:
                try:
                    user_id: int = kwargs["user_id"]
                    summary_date = kwargs.get("summary_date") or date.today()

                    # Get summary
                    summary = financial_tools.summary_service.get_account_summary(
                        user_id, summary_date
                    )

                    return f"Financial summary for {summary_date.month}/{summary_date.year}: {summary}"

                except Exception as e:
                    return f"Error getting financial summary: {str(e)}"

        return SummaryQueryTool()

    def get_categories_tool(self) -> BaseTool:
        """Tool for querying user categories"""
        financial_tools = self

        class CategoryQueryTool(BaseTool):
            name: str = "get_categories"
            description: str = """
            Query user categories for organizing transactions. Can filter by
            category type (income/expenses).
            """
            args_schema: type[BaseModel] = CategoryQueryInput

            def _run(self, **kwargs) -> str:
                try:
                    user_id: int = kwargs["user_id"]
                    category_type = kwargs.get("category_type")

                    # Get user categories
                    user_categories = (
                        financial_tools.crud_user_category.get_user_categories(user_id)
                    )

                    # Format response
                    result: list[dict[str, Any]] = []
                    for user_cat in user_categories:
                        category = financial_tools.crud_category.get(
                            user_cat.category_id
                        )
                        if category:
                            if category_type and category.type != category_type:
                                continue

                            result.append(
                                {
                                    "id": category.id,
                                    "name": category.name,
                                    "type": category.type,
                                }
                            )

                    return f"Found {len(result)} categories: {result}"

                except Exception as e:
                    return f"Error querying categories: {str(e)}"

        return CategoryQueryTool()

    def get_all_tools(self) -> list[BaseTool]:
        """Get all available financial tools"""
        return [
            self.get_transactions_tool(),
            self.get_accounts_tool(),
            self.get_summary_tool(),
            self.get_categories_tool(),
        ]
