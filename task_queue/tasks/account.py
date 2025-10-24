from core.exceptions import MissingResource
from crud.account import CRUDAccount
from crud.currency import CRUDCurrency, CRUDUserCurrency
from schemas.account import AccountCreate
from schemas.currency import UserCurrencyCreate
from schemas.enums import AccountCategoryEnum, AccountCategoryEnum, AccountTypeEnum


async def add_default_currency(ctx, user_id):
    crud_currency: CRUDCurrency = ctx["crud_currency"]
    crud_user_currency: CRUDUserCurrency = ctx["crud_user_currency"]
    default_currency = crud_currency.get_currency_by_code("USD")
    if not default_currency:
        raise MissingResource(message="Default currency not found")
    user_currency = UserCurrencyCreate(
        user_id=user_id,
        currency_id=default_currency.id,
        exchange_rate=1.0,
        is_default=True,
    )
    crud_user_currency.create(user_currency)


async def add_default_accounts(ctx, user_id):
    crud_account: CRUDAccount = ctx["crud_account"]
    crud_user_currency: CRUDUserCurrency = ctx["crud_user_currency"]

    # TODO: CONSIDER ADDING A DEFAULT CURRENCY FOR THE USERS
    default_currency = crud_user_currency.get_user_default_currency(user_id)
    if not default_currency:
        raise MissingResource(message="Default currency not found")

    types = [AccountTypeEnum.DEFAULT_PUBLIC, AccountTypeEnum.DEFAULT_PRIVATE]
    for account_type in types:
        account_obj = AccountCreate(
            user_id=user_id,
            account_type=account_type,
            account_category=AccountCategoryEnum.BALANCE,
            amount=0,
            user_currency_id=default_currency.id,
            name=(
                "Default Account"
                if account_type == AccountTypeEnum.DEFAULT_PUBLIC
                else "Private Account"
            ),
            amount_base=0,
        )
        crud_account.create(account_obj)
