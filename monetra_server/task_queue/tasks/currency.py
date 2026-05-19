from tarsq import task

from monetra_server.core.exceptions import MissingResource
from monetra_server.crud.currency import CRUDCurrency, CRUDUserCurrency
from monetra_server.schemas.currency import UserCurrencyUpdate
from monetra_server.utils.currency_conversion import change_default_currency
from monetra_server.utils.helper import convert_sql_models_to_dict


@task("update_currencies_exchange_rate")
async def update_currencies_exchange_rate(ctx, payload: dict):

    currency_code = payload["currency_code"]
    user_id = payload["user_id"]

    crud_user_currency: CRUDUserCurrency = ctx["crud_user_currency"]()

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
