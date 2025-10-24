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
from utils.currency_conversion import to_minor_units


class AccountService:
    def __init__(
        self,
        crud_account: CRUDAccount,
        crud_user_currency: CRUDUserCurrency,
        crud_currency: CRUDCurrency,
    ):
        self.crud_account = crud_account
        self.crud_user_currency = crud_user_currency
        self.crud_currency = crud_currency

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

        currency = self.crud_user_currency.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        if not currency:
            currency = self.crud_user_currency.get_user_default_currency(user_id)
        data_obj.user_currency_id = currency.id
        data_obj.amount_base = to_minor_units(data_obj.amount, currency.currency.code)
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

        currency = self.crud_user_currency.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        if not currency:
            raise MissingResource(message="User currency not found")

        data_obj.amount_base = to_minor_units(data_obj.amount, currency.currency.code)
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

        user_currencies = self.crud_user_currency.get_user_currencies(user_id)
        if not user_currencies:
            raise MissingResource(message="Default currency not found")
        default_currency = max(user_currencies, key=lambda x: x.is_default)
        total_amount = []
        for currency in user_currencies:
            for account in accounts:
                if account.user_currency_id == currency.id:
                    total_amount.append(
                        account.amount  # Let's say this is 1500 Naira
                        * default_currency.exchange_rate  # Default rate is one...
                        / currency.exchange_rate  # Exchange rate is 0.007
                    )
        total_amount = sum(total_amount)
        return {
            "total_balance": total_amount,
            "accounts": accounts,
        }
