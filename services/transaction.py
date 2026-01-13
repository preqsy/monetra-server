from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Tuple
from arq import ArqRedis
from sqlalchemy import Column
from core.exceptions import MissingResource
from core.externals.mono.mono_client import MonoClient
from core.externals.schema import MonoTransactionSchema
from core.topics.transactions import TRANSACTION_CREATED
from crud.account import CRUDAccount
from crud.category import CRUDCategory, CRUDUserCategory
from crud.currency import CRUDUserCurrency
from crud.rules import CRUDRules
from crud.transaction import CRUDTransaction
from models.account import Account
from models.category import Category, UserCategory
from models.currency import UserCurrency
from models.kafka_models import TransactionDoc
from models.rules import TransactionRule
from models.transaction import Transaction
from schemas.account import MonoAccountCreate
from schemas.enums import AccountTypeEnum, MonoTransactionTypeEnum, TransactionTypeEnum
from schemas.transaction import MonoTransactionCreate, TransactionCreate
from services.account import AccountService
from services.category import CategoryService
from services.currency import CurrencyService
from services.kafka_producer import publish
from utils.currency_conversion import from_minor_units, to_minor_units
from utils.helper import convert_sql_models_to_dict, extract_beneficiary


class TransactionService:
    def __init__(
        self,
        crud_transaction: CRUDTransaction,
        queue_connection: ArqRedis,
        crud_user_currency: CRUDUserCurrency,
        crud_account: CRUDAccount,
        crud_user_category: CRUDUserCategory,
        mono_client: MonoClient,
        crud_rules: CRUDRules,
        crud_category: CRUDCategory,
        currency_service=CurrencyService,
        account_service=AccountService,
        category_service=CategoryService,
    ):
        self.crud_transaction = crud_transaction
        self.queue_connection = queue_connection
        self.crud_user_currency = crud_user_currency
        self.crud_account = crud_account
        self.crud_user_category = crud_user_category
        self.mono_client = mono_client
        self.crud_rules = crud_rules
        self.crud_category = crud_category
        self.currency_service = currency_service
        self.account_service = account_service
        self.category_service = category_service

    async def create_transaction(
        self, data_obj: TransactionCreate, user_id: Column[int]
    ) -> Transaction:
        if (
            data_obj.amount < 0
            and data_obj.transaction_type == TransactionTypeEnum.INCOME
        ):
            # data_obj.amount = 0
            data_obj.amount = abs(data_obj.amount)

        elif (
            data_obj.amount < 0
            and data_obj.transaction_type == TransactionTypeEnum.EXPENSE
        ):
            data_obj.amount = abs(data_obj.amount)
        user_currency, _ = await self.currency_service.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        data_obj.user_currency_id = user_currency.id  # type: ignore

        data_obj.account_id = await self.account_service.validate_user_account(
            user_id=user_id, account_id=data_obj.account_id, is_paid=data_obj.is_paid  # type: ignore
        )

        data_obj.amount = to_minor_units(
            amount=data_obj.amount, currency=user_currency.currency.code  # type: ignore
        )
        data_obj.amount_in_default = data_obj.amount

        data_obj.user_id = user_id
        data_obj.date = (
            datetime.now(timezone.utc) if not data_obj.date else data_obj.date
        )
        category = await self.category_service.validate_user_category(user_id, data_obj.category_id)  # type: ignore
        data_obj.category_id = category.category_id  # type: ignore
        transaction = self.crud_transaction.create(data_obj)

        await self._publish_created_transaction(transaction)
        return transaction

    async def list_user_transactions(
        self, user_id: int, date: date
    ) -> List[Transaction]:
        transactions = self.crud_transaction.get_user_transactions_by_id(user_id, date)
        transactions = [convert_sql_models_to_dict(t) for t in transactions]

        for trans in transactions:
            account_currency = trans["user_currency"]["exchange_rate"]
            amount = Decimal(trans["amount_in_default"])
            rate = Decimal(str(account_currency))

            trans["amount_in_default"] = (amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return transactions

    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        transaction = self.crud_transaction.get_transaction_by_id(
            transaction_id, user_id
        )
        if transaction:
            return self.crud_transaction.delete(transaction_id)
        raise MissingResource(message="Transaction not found or access denied.")

    async def get_one_account_transactions(
        self, account_id: int, user_id: int
    ) -> List[Transaction]:
        account = self.crud_account.get_account_by_id(
            account_id=account_id, user_id=user_id
        )
        if not account:
            raise MissingResource(message="Account not found or access denied.")
        return self.crud_transaction.get_transactions_by_account_id(
            account_id=account_id, user_id=user_id
        )

    async def get_single_transaction(
        self, transaction_id: int, user_id: int
    ) -> Transaction:
        transaction = self.crud_transaction.get_transaction_by_id(
            transaction_id, user_id
        )
        if not transaction:
            raise MissingResource(message="Transaction not found or access denied.")
        transaction = convert_sql_models_to_dict(transaction)
        account_currency = transaction["user_currency"]["exchange_rate"]
        amount = Decimal(transaction["amount_in_default"])
        rate = Decimal(str(account_currency))
        transaction["amount_in_default"] = (amount / rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return transaction

    async def calculate_total_income_and_expenses(
        self, user_id: int
    ) -> Dict[str, Decimal]:
        transactions = self.crud_transaction.get_all_transactions_by_user_id(
            user_id=user_id
        )
        transactions = [convert_sql_models_to_dict(t) for t in transactions]

        for trans in transactions:
            transaction_currency_exchange_rate = trans["user_currency"]["exchange_rate"]
            amount = Decimal(trans["amount_in_default"])
            rate = Decimal(str(transaction_currency_exchange_rate))
            trans["amount_in_default"] = (amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        income = sum(
            [
                Decimal(trans["amount_in_default"])
                for trans in transactions
                if trans["transaction_type"] == "income"
            ]
        )
        expense = sum(
            [
                Decimal(trans["amount_in_default"])
                for trans in transactions
                if trans["transaction_type"] == "expense"
            ]
        )
        return {
            "total_income": income or Decimal(0),
            "total_expense": expense or Decimal(0),
        }

    async def create_mono_transactions(
        self,
        mono_account_id: str,
        user_id: int,
        account_id: int,
        start_date: date = None,
    ) -> None:
        user_currency, user_default_currency = (
            await self.currency_service.get_user_currency(
                user_id=user_id,
                user_currency_id=None,
            )
        )
        transactions = await self.get_deduped_transactions(
            mono_account_id=mono_account_id,
            user_id=user_id,
            start_date=start_date,
        )
        if not transactions:
            return
        income_category, expense_category = (
            self.crud_category.get_uncategorized_income_and_expense()
        )
        type_map = {
            MonoTransactionTypeEnum.CREDIT: TransactionTypeEnum.INCOME,
            MonoTransactionTypeEnum.DEBIT: TransactionTypeEnum.EXPENSE,
        }

        user_rules = (
            self.crud_rules.list_rules_by_user_id(user_id) if self.crud_rules else []
        )
        transaction_objs = await self._prepare_transaction_data(
            transactions=transactions,
            user_currency=user_currency,
            user_default_currency=user_default_currency,
            user_id=user_id,
            account_id=account_id,
            user_rules=user_rules,
            income_category=income_category,
            expense_category=expense_category,
            type_map=type_map,
        )
        self.crud_transaction.bulk_insert(transaction_objs)
        self.crud_account.update(
            id=account_id,
            data_obj={MonoAccountCreate.LAST_SYNC_DATE: datetime.now(timezone.utc)},
        )

    async def _prepare_transaction_data(
        self,
        *,
        transactions: List[MonoTransactionSchema],
        user_currency: UserCurrency,
        user_default_currency: UserCurrency,
        user_id: Column[int],
        account_id: Column[int],
        user_rules: List[TransactionRule],
        income_category: Category,
        expense_category: Category,
        type_map: Dict[MonoTransactionTypeEnum, TransactionTypeEnum],
    ) -> List[Dict]:
        prepared_transactions = []
        rules_map = {rule.beneficiary_name: rule.category_id for rule in user_rules}

        for transaction in transactions:
            amount = from_minor_units(transaction.amount, transaction.currency)
            amount_in_default = amount / user_currency.exchange_rate
            amount_in_default = to_minor_units(
                amount_in_default, user_default_currency.currency.code
            )
            # Extract beneficiary name from narration
            beneficiary_name = extract_beneficiary(transaction.narration)
            category_id = None
            if beneficiary_name:
                category_id = rules_map.get(beneficiary_name)
            if not category_id:
                # Use default if no rule matched
                category_id = (
                    income_category.id
                    if transaction.type == MonoTransactionTypeEnum.CREDIT
                    else expense_category.id
                )

            prepared_transactions.append(
                MonoTransactionCreate(
                    **transaction.model_dump(),
                    mono_transaction_id=transaction.id,
                    mono_type=transaction.type,
                    account_id=account_id,
                    transaction_type=type_map.get(
                        transaction.type, TransactionTypeEnum.DEFAULT
                    ),
                    user_id=user_id,
                    user_currency_id=user_currency.id,
                    amount_in_default=amount_in_default,
                    category_id=category_id,
                ).model_dump()
            )
        return prepared_transactions

    async def _publish_created_transaction(self, transaction: Transaction):
        event_dict = TransactionDoc(
            doc_id=transaction.id,  # type: ignore
            doc_type="transaction",
            user_id=transaction.user_id,  # type: ignore
            transaction_id=transaction.id,  # type: ignore
            account_id=transaction.account_id,  # type: ignore
            category=transaction.category.name.lower(),
            amount=transaction.amount,  # type: ignore
            # date_utc=transaction.created_at,
            category_id=transaction.category_id,  # type: ignore
            currency=transaction.user_currency.currency.code,
            transaction_type=transaction.transaction_type,
        ).model_dump()
        print(f"Event dict: {event_dict}")
        print(f"Publishing to topic: {TRANSACTION_CREATED}")
        publish(event=event_dict, topic=TRANSACTION_CREATED)

    async def get_deduped_transactions(
        self,
        mono_account_id: str,
        user_id: int,
        start_date: date = None,
    ) -> List[Transaction]:

        new_transactions = await self.mono_client.get_transactions(
            account_id=mono_account_id,
            start_date=start_date,
        )
        old_transactions = self.crud_transaction.get_automatic_transactions(
            user_id=user_id
        )

        existing_mono_transaction_ids = [
            t.mono_transaction_id for t in old_transactions if t.mono_transaction_id
        ]
        deduped_transactions = [
            t for t in new_transactions if t.id not in existing_mono_transaction_ids
        ]

        return deduped_transactions
