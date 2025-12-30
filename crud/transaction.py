from datetime import datetime, date
from core.db import get_db
from crud.base import CRUDBase
from models.currency import UserCurrency
from models.transaction import Transaction
from sqlalchemy.orm import joinedload
from sqlalchemy import extract

from schemas.enums import AccountTypeEnum, TransactionTypeEnum


class CRUDTransaction(CRUDBase[Transaction]):

    def _get_transaction_query_by_user_id(self, user_id: int):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.account.has(is_deleted=False),
            )
            .options(
                joinedload(Transaction.category),
                joinedload(Transaction.user_currency).joinedload(UserCurrency.currency),
                joinedload(Transaction.account),
            )
            .order_by(Transaction.id.desc())
        )

    def get_user_transactions_by_id(self, user_id: int, date: date):
        month = date.month
        year = date.year
        return (
            self._get_transaction_query_by_user_id(user_id)
            .filter(
                extract("month", Transaction.created_at) == month,
                extract("year", Transaction.created_at) == year,
            )
            .all()
        )

    def get_all_transactions_by_user_id(self, user_id: int):
        return self._get_transaction_query_by_user_id(user_id).all()

    def get_transaction_by_id(self, transaction_id: int, user_id: int):
        return (
            self._get_transaction_query_by_user_id(user_id)
            .filter(Transaction.id == transaction_id)
            .first()
        )

    def get_automatic_transactions(self, user_id: int):
        return (
            self._get_transaction_query_by_user_id(user_id)
            .filter(Transaction.account.has(account_type=AccountTypeEnum.AUTOMATIC))
            .all()
        )

    def get_transactions_by_account_id(self, account_id: int, user_id: int):
        return (
            self._get_transaction_query_by_user_id(user_id)
            .filter(Transaction.account_id == account_id)
            .all()
        )

    def _get_transaction_object_by_category_id(self, category_id: int, user_id: int):
        return self._get_transaction_query_by_user_id(user_id).filter(
            Transaction.category_id == category_id,
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
            # Transaction.transaction_type == type,
        )

        return query.all()

    def get_transactions_by_category_ids(
        self,
        user_id: int,
        category_ids: list[int],
        transaction_date: datetime = None,
    ) -> list[Transaction]:
        query = self._get_transaction_query_by_user_id(user_id).filter(
            Transaction.category_id.in_(category_ids)
        )
        if transaction_date:
            query = query.filter(Transaction.date >= transaction_date)
        return query.all()
        # )

    async def get_transaction_by_type_and_date(
        self,
        user_id: int,
        transaction_date: datetime,
        type: TransactionTypeEnum,
    ):
        return (
            self._get_transaction_query_by_user_id(user_id)
            .filter(
                Transaction.date >= transaction_date,
                Transaction.transaction_type == type,
            )
            .all()
        )


db_session = next(get_db())


def get_crud_transaction() -> CRUDTransaction:
    return CRUDTransaction(model=Transaction, db=db_session)
