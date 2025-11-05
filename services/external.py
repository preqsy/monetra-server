from datetime import date

from arq import ArqRedis
from core.exceptions import MissingResource, ResourceExists
from core.externals.exchange_rate.exchangerate_api import get_exchange_rate
from core.externals.mono.mono_client import MonoClient
from core.externals.plaid.plaid_client import PlaidClient
from crud.account import CRUDAccount
from crud.currency import (
    CRUDCurrency,
    CRUDUserCurrency,
)
from crud.user import CRUDAuthUser
from models.user import User
from schemas.account import MonoAccountCreate
from schemas.currency import UserCurrencyCreate
from utils.currency_conversion import from_minor_units


class ExternalService:
    def __init__(
        self,
        plaid_client: PlaidClient,
        mono_client: MonoClient,
        crud_account: CRUDAccount,
        queue_connection: ArqRedis,
        crud_currency: CRUDCurrency,
        crud_user_currency: CRUDUserCurrency,
        crud_user: CRUDAuthUser,
    ):
        self.plaid_client = plaid_client
        self.mono_client = mono_client
        self.crud_account = crud_account
        self.queue_connection = queue_connection
        self.crud_currency = crud_currency
        self.crud_user_currency = crud_user_currency
        self.crud_user = crud_user

    async def mono_exchange_code(
        self,
        code: str,
        user: User,
        transaction_start_date: date = None,
    ):

        result = await self.mono_client.exchange_code(code)

        # account = await self.mono_client.get_account(account_id=code)
        account = await self.mono_client.get_account(account_id=result["data"]["id"])

        if self.crud_account.get_by_account_number(account.account.account_number):
            raise ResourceExists(message="Account with account number already exists")

        amount = from_minor_units(account.account.balance, account.account.currency)

        currency = self.crud_currency.get_currency_by_code(
            code=account.account.currency
        )
        if not currency:
            raise MissingResource(message="Currency not found")
        user_currencies = self.crud_user_currency.get_user_currencies(user_id=user.id)
        user_currency = next(
            (uc for uc in user_currencies if uc.currency_id == currency.id), None
        )
        default_currency = max(user_currencies, key=lambda uc: uc.is_default)

        currency_rates = await get_exchange_rate(default_currency.currency.code)
        exchange_rate = currency_rates.get(currency.code, 1)
        if not user_currency:
            user_currency_obj = UserCurrencyCreate(
                user_id=user.id,
                currency_id=currency.id,
                exchange_rate=exchange_rate,
                is_default=False,
            )

            user_currency = self.crud_user_currency.create(user_currency_obj)
        account_data = MonoAccountCreate(
            user_id=user.id,
            name=account.account.institution.name or "Account",
            user_currency_id=user_currency.id,
            amount=amount,
            amount_in_default=account.account.balance,
            account_number=account.account.account_number,
            ext_account_id=account.account.id,
        )
        new_account = self.crud_account.create(account_data.model_dump())
        self.crud_user.update(user.id, {"mono_customer_id": account.customer.id})
        await self.queue_connection.enqueue_job(
            "retrieve_user_mono_transactions",
            account_id=new_account.id,
            start_date=transaction_start_date,
            user_id=user.id,
            mono_account_id=account.account.id,
        )
        return account_data

    async def plaid_create_link_token(
        self,
        user_id: int,
    ):
        result = await self.plaid_client.create_link_token(user_id)

        return result

    async def plaid_exchange_public_token(self, public_token: str, user_id: int = 1):
        # Exchange public token for access token
        exchange_result = await self.plaid_client.exchange_public_token(public_token)
        access_token = exchange_result.access_token

        plaid_accounts_response = await self.plaid_client.get_accounts(access_token)

        created_accounts = self.create_plaid_accounts_from_response(
            plaid_accounts_response, access_token, user_id
        )
        return created_accounts

    def create_plaid_accounts_from_response(
        self,
        plaid_accounts_response,
        access_token,
        user_id: int,
    ):
        from schemas.account import PlaidAccountCreate

        created_accounts = []
        for account in plaid_accounts_response.accounts:
            account_id = getattr(account, "account_id", None) or ""
            name = getattr(account, "name", None) or "Account"
            account_number = None
            if (
                hasattr(plaid_accounts_response.numbers, "ach")
                and plaid_accounts_response.numbers.ach
            ):
                for ach in plaid_accounts_response.numbers.ach:
                    if ach.account_id == account_id:
                        account_number = ach.account
                        break

            balances = getattr(account, "balances", None)
            amount = int(getattr(balances, "current", 0)) if balances else 0
            currency = getattr(balances, "iso_currency_code", None) or "USD"

            if self.crud_account.get_by_account_number(account_number):
                continue
            currency_check = self.crud_currency.get_currency_by_code(currency)

            user_currency = self.crud_user_currency.get_user_currency_by_currency(
                user_id, currency_check.id
            )

            if not user_currency:
                user_currency = self.crud_user_currency.create(
                    {
                        "user_id": user_id,
                        "currency_id": currency_check.id,
                    }
                )

            plaid_account_data = PlaidAccountCreate(
                user_id=user_id,
                access_token=access_token,
                account_number=account_number,
                ext_account_id=account_id,
                name=name,
                user_currency_id=None,
                amount=amount,
                amount_base=amount,
            )
            self.crud_account.create(plaid_account_data.model_dump())
            created_accounts.append(plaid_account_data)
        return created_accounts

    async def get_transactions(
        self,
        access_token: str,
    ):
        result = await self.plaid_client.fetch_transactions(access_token)

        return result
