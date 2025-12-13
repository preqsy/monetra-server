from typing import Optional
from core.db import get_db
from crud.base import CRUDBase
from models.account import Account
from models.currency import UserCurrency
from schemas.enums import AccountTypeEnum
from sqlalchemy.orm import joinedload


class CRUDAccount(CRUDBase[Account]):
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
        return (
            self.db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.is_deleted == False,
            )
            .all()
        )

    def get_public_accounts(self, user_id: int) -> list[Account]:
        return (
            self.db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.account_type != AccountTypeEnum.DEFAULT_PRIVATE,
                Account.is_deleted == False,
            )
            .options(
                joinedload(Account.user_currency).joinedload(UserCurrency.currency)
            )
            .all()
        )

    def get_account_by_id(self, account_id: int, user_id: int) -> Optional[Account]:
        return (
            self.db.query(Account)
            .filter(
                Account.id == account_id,
                Account.user_id == user_id,
                Account.account_type != AccountTypeEnum.DEFAULT_PRIVATE,
                Account.is_deleted == False,
            )
            .first()
        )

    def get_user_default_public_account(self, user_id: str) -> Optional[Account]:
        return (
            self.db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.account_type == AccountTypeEnum.DEFAULT_PUBLIC,
                Account.is_deleted == False,
            )
            .first()
        )

    def get_automatic_accounts(self, user_id: int) -> list[Account]:
        return (
            self.db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.is_deleted == False,
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
