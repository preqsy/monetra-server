from datetime import datetime, timedelta, timezone
from core.exceptions import InvalidRequest
from crud.budget import CRUDBudget
from schemas.budget import BudgetCreate, TotalBudgetCreate
from schemas.enums import BudgetPeriodEnum, BudgetTypeEnum, TransactionTypeEnum
from services.transaction import TransactionService
from utils.currency_conversion import to_minor_units
from utils.helper import convert_sql_models_to_dict


class BudgetService:
    def __init__(
        self,
        crud_budget: CRUDBudget,
        transaction_service: TransactionService,
    ):
        self.crud_budget = crud_budget
        self.transaction_service = transaction_service

    async def create_budget(self, data_obj: BudgetCreate, user_id: int):
        selected_currency, _ = await self.transaction_service.get_user_currency(
            user_id=user_id, user_currency_id=data_obj.user_currency_id
        )
        selected_category = await self.transaction_service.validate_user_category(
            user_id=user_id, category_id=data_obj.category_id
        )
        data_obj.user_id = user_id
        data_obj.category_id = selected_category.category_id
        data_obj.amount = to_minor_units(
            amount=data_obj.amount, currency=selected_currency.currency.code
        )
        data_obj.name = selected_category.category.name
        data_obj.user_currency_id = selected_currency.id

        return self.crud_budget.create(data_obj)

    async def calculate_budget(
        self,
        user_id: int,
        period: BudgetPeriodEnum,
    ):
        budgets = self.crud_budget.get_budget_by_period(user_id=user_id, period=period)

        if not budgets:
            return []

        transaction_date = await self._get_budget_period_start_date(period=period)
        new_budgets = []
        category_ids = [budget.category_id for budget in budgets]
        print(f"Category IDs: {category_ids}")
        for budget in budgets:
            # TODO: Optimize this query later.
            transactions = self.transaction_service.crud_transaction.get_transaction_by_category_id_and_type(
                category_id=budget.category_id,
                user_id=user_id,
                transaction_date=transaction_date,
                type=budget.type,
            )
            transaction_amount_sum = (
                sum(t.amount for t in transactions) if transactions else 0
            )

            budget_dict = convert_sql_models_to_dict(budget)
            budget_dict["spent_amount"] = transaction_amount_sum
            new_budgets.append(budget_dict)
        return new_budgets

    async def get_total_budget(
        self,
        user_id: int,
        period: BudgetPeriodEnum,
        budget_type: BudgetTypeEnum = BudgetTypeEnum.TOTAL,
    ):

        transaction_date = await self._get_budget_period_start_date(period=period)

        budget = self.crud_budget.get_budget_by_period(
            user_id=user_id,
            period=period,
            type=budget_type,
        )
        total_budget = budget.amount if budget else 0

        transactions = await self.transaction_service.crud_transaction.get_transaction_by_type_and_date(
            user_id=user_id,
            type=TransactionTypeEnum.EXPENSE,
            transaction_date=transaction_date,
        )

        total_spent = sum(t.amount for t in transactions) if transactions else 0
        total_budget = {"total_budget": total_budget, "total_spent": total_spent}

        return total_budget

    async def create_total_budget(self, user_id: int, data_obj: TotalBudgetCreate):
        budget = self.crud_budget.get_budget_by_period(
            user_id=user_id,
            period=data_obj.period,
            type=BudgetTypeEnum.TOTAL,
        )
        if budget:
            raise InvalidRequest("Total budget already exists")
        budget = await self.create_budget(
            BudgetCreate(
                amount=data_obj.amount,
                period=data_obj.period,
                type=BudgetTypeEnum.TOTAL,
                category_id=0,
                user_currency_id=data_obj.user_currency_id,
            ),
            user_id=user_id,
        )
        return budget

    async def delete_budget(self, budget_id: int, user_id: int):
        budget = self.crud_budget.get(budget_id)
        if not budget or budget.user_id != user_id:
            raise InvalidRequest("Budget not found")
        return self.crud_budget.delete(budget_id)

    async def _get_budget_period_start_date(self, period: BudgetPeriodEnum):
        today = datetime.now(timezone.utc)
        if period == BudgetPeriodEnum.WEEKLY:
            return today - timedelta(weeks=1)
        elif period == BudgetPeriodEnum.DAILY:
            return today - timedelta(days=1)
        elif period == BudgetPeriodEnum.MONTHLY:
            return today - timedelta(days=30)
        else:
            raise InvalidRequest("Invalid budget type")
