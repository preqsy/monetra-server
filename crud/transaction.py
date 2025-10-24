from datetime import datetime
from crud.base import CRUDBase
from models.transaction import Transaction
from sqlalchemy.orm import joinedload

from schemas.enums import AccountTypeEnum, TransactionTypeEnum


class CRUDTransaction(CRUDBase[Transaction]):
    def get_user_transactions_by_id(self, user_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency),
                joinedload(Transaction.account),
            )
            .all()
        )

    def get_transaction_by_id(self, transaction_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.id == transaction_id,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency, innerjoin=True),
                joinedload(Transaction.account),
            )
            .first()
        )

    def get_automatic_transactions(self, user_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.account.has(account_type=AccountTypeEnum.AUTOMATIC),
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency, innerjoin=True),
                joinedload(Transaction.account),
            )
            .all()
        )

    def get_transactions_by_account_id(self, account_id: int, user_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.user_id == user_id,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency, innerjoin=True),
                joinedload(Transaction.account),
            )
            .all()
        )

    def _get_transaction_object_by_category_id(self, category_id: int, user_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency, innerjoin=True),
                joinedload(Transaction.account),
            )
        )

    def get_transaction_by_category_id(self, category_id: int, user_id: int):
        return self._get_transaction_object_by_category_id(category_id, user_id).all()

    def get_transaction_by_category_id_and_type(
        self,
        user_id: int,
        category_id: int,
        transaction_date: datetime,
        type: str = None,
    ) -> list[Transaction]:
        query = self._get_transaction_object_by_category_id(
            user_id=user_id, category_id=category_id
        ).filter(
            Transaction.date >= transaction_date,
            Transaction.transaction_type == type,
        )

        return query.all()

    async def get_transaction_by_type_and_date(
        self,
        user_id: int,
        transaction_date: datetime,
        type: TransactionTypeEnum,
    ):
        query = (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.date >= transaction_date,
                Transaction.transaction_type == type,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency, innerjoin=True),
                joinedload(Transaction.account),
            )
        )
        return query.all()


def get_crud_transaction() -> CRUDTransaction:
    return CRUDTransaction(model=Transaction)
