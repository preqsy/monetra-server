from decimal import Decimal
from sqlalchemy import Column
from core.exceptions import MissingResource
from crud.category import (
    CRUDCategory,
    CRUDUserCategory,
)
from crud.currency import CRUDUserCurrency
from crud.planner import CRUDPlanner
from schemas.category import CategoryCreate
from schemas.enums import PlannerTypeEnum, TransactionTypeEnum
from schemas.planner import PlannerAmountUpdate, PlannerCreate, PlannerUpdate
from schemas.transaction import TransactionCreate
from services.category import CategoryService
from services.transaction import TransactionService
from utils.currency_conversion import to_minor_units
from utils.helper import convert_sql_models_to_dict


class PlannerService:
    def __init__(
        self,
        crud_planner: CRUDPlanner,
        crud_user_currency: CRUDUserCurrency,
        crud_category: CRUDCategory,
        crud_user_category: CRUDUserCategory,
        transaction_service: TransactionService,
        category_service: CategoryService,
    ):
        self.crud_planner = crud_planner
        self.crud_user_currency = crud_user_currency
        self.crud_category = crud_category
        self.crud_user_category = crud_user_category
        self.category_service = category_service
        self.transaction_service = transaction_service

    async def create_planner(self, user_id: int, data_obj: PlannerCreate):
        (
            user_currency,
            user_default_currency,
        ) = await self.transaction_service.get_user_currency(
            user_id=user_id, user_currency_id=data_obj.user_currency_id
        )

        required_amount_default = data_obj.required_amount / user_currency.exchange_rate

        accumulated_amount_in_default = (
            data_obj.accumulated_amount / user_currency.exchange_rate
        )

        data_obj.required_amount = to_minor_units(
            amount=data_obj.required_amount, currency=user_currency.currency.code
        )
        data_obj.accumulated_amount = to_minor_units(
            amount=data_obj.accumulated_amount, currency=user_currency.currency.code
        )
        data_obj.required_amount_in_default = to_minor_units(
            amount=required_amount_default,
            currency=user_default_currency.currency.code,
        )
        data_obj.accumulated_amount_in_default = to_minor_units(
            amount=accumulated_amount_in_default,
            currency=user_default_currency.currency.code,
        )

        category_obj = CategoryCreate(
            name=data_obj.name,
            type=data_obj.type,
        )
        category = await self.category_service.create_user_category(
            data_obj=category_obj, user_id=user_id
        )
        data_obj.category_id = category.id
        if data_obj.type == PlannerTypeEnum.GOAL:
            data_obj.role = None
        data_obj.account_id = await self.transaction_service.validate_user_account(
            user_id=user_id, account_id=data_obj.account_id
        )
        data_obj.user_id = user_id
        data_obj.image = str(data_obj.image) if data_obj.image else None
        data_obj.user_currency_id = user_currency.id
        # data_obj.date = data_obj.date if data_obj.date else date.today()
        return self.crud_planner.create(data_obj)

    async def get_user_planners(
        self, user_id: Column[int], type_query: PlannerTypeEnum | None
    ):
        planners = self.crud_planner.get_planner_by_user_id(user_id=user_id)
        if type_query:
            planners = [p for p in planners if p.type == type_query]
        planners = [convert_sql_models_to_dict(p) for p in planners]
        new_planners = []
        for planner in planners:
            selected_currency, _ = await self.transaction_service.get_user_currency(
                user_id=user_id, user_currency_id=planner["user_currency_id"]
            )
            required_amount_in_default = Decimal(planner["required_amount"])
            accumulated_amount_in_default = Decimal(planner["accumulated_amount"])
            rate = Decimal(str(selected_currency.exchange_rate))

            planner["required_amount_in_default"] = (
                required_amount_in_default / rate
            ).quantize(Decimal("0.01"))

            planner["accumulated_amount_in_default"] = (
                accumulated_amount_in_default / rate
            ).quantize(Decimal("0.01"))
            new_planners.append(planner)
        return new_planners

    async def get_single_planner(self, user_id: Column[int], id: int):
        planner = self.crud_planner.get_planner_by_id(id=id)
        if not planner or planner.user_id != user_id:
            raise MissingResource(message="Planner not found")
        transactions = (
            self.transaction_service.crud_transaction.get_transaction_by_category_id(
                category_id=planner.category_id,
                user_id=user_id,
            )
        )
        planner = convert_sql_models_to_dict(planner)
        planner["transactions"] = transactions
        return planner

    async def update_planner_amount(
        self, user_id: Column[int], id: int, data_obj: PlannerAmountUpdate
    ):
        print(f"User currency id:{data_obj.user_currency_id}")
        print(f"Account id:{data_obj.account_id}")
        planner = self.crud_planner.get_planner_by_id(id=id)
        if not planner or planner.user_id != user_id:
            raise MissingResource(message="Planner not found")

        transaction_amount = data_obj.accumulated_amount
        selected_currency, default_currency = (
            await self.transaction_service.get_user_currency(
                user_id=user_id, user_currency_id=data_obj.user_currency_id
            )
        )

        # Update accumulated amount
        data_obj.accumulated_amount = (
            data_obj.accumulated_amount
            * planner.user_currency.exchange_rate
            / selected_currency.exchange_rate
        )

        data_obj.accumulated_amount = to_minor_units(
            amount=data_obj.accumulated_amount,
            currency=planner.user_currency.currency.code,
        )

        data_obj.accumulated_amount = (
            planner.accumulated_amount + data_obj.accumulated_amount
        )
        data_obj.accumulated_amount_in_default = (
            data_obj.accumulated_amount / selected_currency.exchange_rate
        )
        data_obj.accumulated_amount_in_default = to_minor_units(
            amount=data_obj.accumulated_amount_in_default,
            currency=default_currency.currency.code,
        )
        if data_obj.account_id:
            data_obj.account_id = await self.transaction_service.validate_user_account(
                user_id=user_id, account_id=data_obj.account_id
            )
        await self._create_planner_transaction(
            user_id=user_id,
            amount=transaction_amount,
            account_id=data_obj.account_id,
            category_id=planner.category_id,
            user_currency_id=planner.user_currency_id,
        )
        del data_obj.user_currency_id
        return self.crud_planner.update(id=id, data_obj=data_obj)

    async def update_planner(self, data_obj: PlannerUpdate, id: int, user_id: int):
        planner = self.crud_planner.get_planner_by_id(id=id)
        if not planner or planner.user_id != user_id:
            raise MissingResource(message="Planner not found")
        if data_obj.name:
            category = self.crud_category.get(id=planner.category_id)
            if not category:
                raise MissingResource(message="Category not found")
            if category.name != data_obj.name.title():
                self.crud_category.update(
                    id=category.id, data_obj={PlannerUpdate.NAME: data_obj.name.title()}
                )
        if data_obj.required_amount_in_default > 0 and data_obj.required_amount <= 0:
            data_obj.required_amount_in_default = planner.required_amount_in_default

        if data_obj.required_amount > 0:
            required_amount_in_default = (
                data_obj.required_amount / planner.user_currency.exchange_rate
            )
            data_obj.required_amount = to_minor_units(
                amount=data_obj.required_amount,
                currency=planner.user_currency.currency.code,
            )
            data_obj.required_amount_in_default = to_minor_units(
                amount=required_amount_in_default,
                currency=planner.user_currency.currency.code,
            )
        return self.crud_planner.update(id=id, data_obj=data_obj)

    async def _create_planner_transaction(
        self,
        user_id: int,
        amount: int,
        account_id: int,
        category_id: int,
        user_currency_id: int,
    ):

        transaction_obj = TransactionCreate(
            amount=amount,
            account_id=account_id,
            category_id=category_id,
            user_currency_id=user_currency_id,
            user_id=user_id,
            transaction_type=(
                TransactionTypeEnum.EXPENSE
                if amount > 0
                else TransactionTypeEnum.INCOME
            ),
        )
        await self.transaction_service.create_transaction(
            data_obj=transaction_obj,
            user_id=user_id,
        )
