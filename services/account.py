from decimal import ROUND_HALF_UP, Decimal
from sqlalchemy import Column
from core.exceptions import MissingResource
from crud.account import CRUDAccount
from crud.currency import (
    CRUDCurrency,
    CRUDUserCurrency,
)
from models.account import Account
from schemas.account import AccountCreate
from schemas.enums import AccountCategoryEnum, AccountTypeEnum
from services.transaction import TransactionService
from utils.currency_conversion import to_minor_units
from utils.helper import convert_sql_models_to_dict, extract_beneficiary


class AccountService:
    def __init__(
        self,
        crud_account: CRUDAccount,
        crud_user_currency: CRUDUserCurrency,
        crud_currency: CRUDCurrency,
        transaction_service: TransactionService,
    ):
        self.crud_account = crud_account
        self.crud_user_currency = crud_user_currency
        self.crud_currency = crud_currency
        self.transaction_service = transaction_service

    async def create_account(
        self,
        *,
        data_obj: AccountCreate,
        user_id: Column[int],
    ) -> Account:
        if data_obj.amount < 0:
            data_obj.account_category = AccountCategoryEnum.CREDIT

        if data_obj.credit_amount < 0:
            data_obj.credit_amount = 0

        # Check user currency
        user_currency = self.crud_user_currency.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        if not user_currency:
            user_currency = self.crud_user_currency.get_user_default_currency(user_id)
        data_obj.user_currency_id = user_currency.id
        data_obj.amount = to_minor_units(data_obj.amount, user_currency.currency.code)
        data_obj.amount_in_default = data_obj.amount
        data_obj.user_id = user_id
        data_obj.account_type = AccountTypeEnum.MANUAL
        return self.crud_account.create(data_obj.model_dump())

    async def update_account(
        self, account_id: int, data_obj: AccountCreate, user_id: int
    ) -> Account:
        account = self.crud_account.get_account_by_id(
            account_id=account_id, user_id=user_id
        )
        if not account:
            raise MissingResource(message="Account not found")

        if data_obj.amount < 0:
            data_obj.account_category = AccountCategoryEnum.CREDIT

        if data_obj.credit_amount < 0:
            data_obj.credit_amount = 0

        user_currency = self.crud_user_currency.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        if not user_currency:
            raise MissingResource(message="User currency not found")

        data_obj.amount = to_minor_units(data_obj.amount, user_currency.currency.code)
        return self.crud_account.update(id=account_id, data_obj=data_obj)

    async def delete_account(self, account_id: int, user_id: int) -> Account:
        account = self.crud_account.get_account_by_id(
            account_id=account_id, user_id=user_id
        )
        if not account:
            raise MissingResource(message="Account not found")
        return self.crud_account.update(
            id=account_id, data_obj={AccountCreate.IS_DELETED: True}
        )

    async def list_accounts(self, user_id: int):
        accounts = self.crud_account.get_public_accounts(user_id=user_id)
        accounts = [convert_sql_models_to_dict(account) for account in accounts]

        total_balance = await self.calculate_account_balance(user_id=user_id)

        return {"total_balance": total_balance, "accounts": accounts}

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
