from typing import List, Optional
from core.db import get_db
from crud.base import CRUDBase
from models.currency import Currency, UserCurrency
from sqlalchemy.orm import joinedload

from schemas.currency import UserCurrencyUpdate


class CRUDCurrency(CRUDBase):
    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        return self.db.query(Currency).filter(Currency.code == code.upper()).first()

    def get_currency_by_id(self, id: int) -> Optional[Currency]:
        return self.db.query(Currency).filter(Currency.id == id).first()

    def get_all_currencies(self) -> List[Currency]:
        return self.db.query(Currency).all()


class CRUDUserCurrency(CRUDBase[UserCurrency]):
    # TODO: Add a relationship to the currency table here
    def get_user_currencies(self, user_id: int):
        return (
            self.db.query(UserCurrency)
            .filter(
                UserCurrency.user_id == user_id,
            )
            .options(joinedload(UserCurrency.currency))
            .all()
        )

    def get_user_currency(self, user_id: int, user_currency_id: int):
        return (
            self.db.query(UserCurrency)
            .filter(
                UserCurrency.user_id == user_id,
                UserCurrency.id == user_currency_id,
            )
            .options(joinedload(UserCurrency.currency))
            .first()
        )

    def get_user_currency_by_currency(self, user_id: int, currency_id: int):
        return (
            self.db.query(UserCurrency)
            .filter(
                UserCurrency.user_id == user_id,
                UserCurrency.currency_id == currency_id,
            )
            .options(joinedload(UserCurrency.currency))
            .first()
        )

    def get_user_default_currency(self, user_id: int):
        return (
            self.db.query(UserCurrency)
            .filter(
                UserCurrency.user_id == user_id,
                UserCurrency.is_default == True,
            )
            .options(joinedload(UserCurrency.currency))
            .first()
        )

    def update_by_user_id(self, user_id: int, data_obj: UserCurrencyUpdate):
        self.db.query(UserCurrency).filter(UserCurrency.user_id == user_id).update(
            data_obj.model_dump(exclude_unset=True)
        )
        self.db.commit()
        return data_obj.model_dump()


db_session = next(get_db())


def get_crud_currency():
    return CRUDCurrency(model=Currency, db=db_session)


def get_crud_user_currency():
    return CRUDUserCurrency(model=UserCurrency, db=db_session)
