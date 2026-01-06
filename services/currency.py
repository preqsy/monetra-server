from arq import ArqRedis
from core.exceptions import MissingResource, ResourceExists
from crud.currency import (
    CRUDCurrency,
    CRUDUserCurrency,
)
from schemas.currency import UserCurrencyCreate, UserCurrencyUpdate


class CurrencyService:
    def __init__(
        self,
        crud_currency: CRUDCurrency,
        crud_user_currency: CRUDUserCurrency,
        queue_connection: ArqRedis,
    ):
        self.crud_currency = crud_currency
        self.crud_user_currency = crud_user_currency
        self.queue_connection = queue_connection

    # TODO: Add a currency check here and also update other currencies to false if is_default is true
    async def add_currency(self, *, data_obj: UserCurrencyCreate, user_id: int):
        currency = self.crud_currency.get(data_obj.currency_id)

        if not currency:
            raise MissingResource(message="Currency not found")
        if self.crud_user_currency.get_user_currency_by_currency_id(
            user_id, data_obj.currency_id
        ):
            raise ResourceExists(message="Currency already added")

        if data_obj.is_default:
            self.crud_user_currency.update_by_user_id(
                user_id=user_id, data_obj=UserCurrencyUpdate(is_default=False)
            )
            await self.queue_connection.enqueue_job(
                "update_currencies_exchange_rate", user_id, currency.code
            )
        data_obj.user_id = user_id
        currency = self.crud_user_currency.create(data_obj.model_dump())
        return currency

    async def update_default_currency(self, user_id: int, data_obj: UserCurrencyUpdate):
        user_currency = self.crud_user_currency.get_user_currency(user_id, data_obj.id)
        if not user_currency:
            raise MissingResource(message="User currency not found")

        if data_obj.is_default and not user_currency.is_default:
            self.crud_user_currency.update_by_user_id(
                user_id=user_id, data_obj=UserCurrencyUpdate(is_default=False)
            )

            await self.queue_connection.enqueue_job(
                "update_currencies_exchange_rate", user_id, user_currency.currency.code
            )
        self.crud_user_currency.update(id=data_obj.id, data_obj=data_obj)

        return user_currency
