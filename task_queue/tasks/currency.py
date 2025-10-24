from core.exceptions import MissingResource
from crud.currency import CRUDCurrency, CRUDUserCurrency
from schemas.currency import UserCurrencyUpdate
from utils.currency_conversion import change_default_currency
from utils.helper import convert_sql_models_to_dict


async def update_currencies_exchange_rate(ctx, user_id, currency_code: str):
    crud_user_currency: CRUDUserCurrency = ctx["crud_user_currency"]

    user_currencies = crud_user_currency.get_user_currencies(user_id)
    if not user_currencies:
        raise MissingResource(message="User currencies not found")

    # Change the default currency
    updated_rates = change_default_currency(
        [convert_sql_models_to_dict(c) for c in user_currencies],
        currency_code,
    )
    # pprint(f"These are the updated rates: {updated_rates}")

    for rates in updated_rates:
        user_currency_update = UserCurrencyUpdate(
            exchange_rate=rates["exchange_rate"],
        )
        crud_user_currency.update(id=rates["id"], data_obj=user_currency_update)
