from typing import Optional
from core.db import get_db
from crud.base import CRUDBase
from models.account import Account
from models.currency import UserCurrency
from schemas.enums import AccountTypeEnum
from sqlalchemy.orm import joinedload


class CRUDAccount(CRUDBase[Account]):

    def _get_account_query_by_user_id(self, user_id: int):
        return self.db.query(Account).filter(
            Account.user_id == user_id,
            Account.is_deleted == False,
        )

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        return (
            self.db.query(Account)
            .filter(
                Account.account_number == account_number,
                Account.is_deleted == False,
            )
            .first()
        )

    def get_accounts(self, user_id: int) -> list[Account]:
        return self._get_account_query_by_user_id(user_id).all()

    def get_public_accounts(self, user_id: int) -> list[Account]:
        return (
            self._get_account_query_by_user_id(user_id)
            .filter(Account.account_type != AccountTypeEnum.DEFAULT_PRIVATE)
            .options(
                joinedload(Account.user_currency).joinedload(UserCurrency.currency)
            )
            .all()
        )

    def get_account_by_id(self, account_id: int, user_id: int) -> Optional[Account]:
        return (
            self._get_account_query_by_user_id(user_id)
            .filter(
                Account.id == account_id,
                Account.account_type != AccountTypeEnum.DEFAULT_PRIVATE,
            )
            .first()
        )

    def get_automatic_accounts(self, user_id: int) -> list[Account]:
        return (
            self._get_account_query_by_user_id(user_id)
            .filter(
                Account.account_type == AccountTypeEnum.AUTOMATIC,
            )
            .all()
        )


db_session = next(get_db())


def get_crud_account() -> CRUDAccount:
    return CRUDAccount(
        model=Account,
        db=db_session,
    )
