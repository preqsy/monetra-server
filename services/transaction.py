from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Tuple
from arq import ArqRedis
from sqlalchemy import Column
from core.exceptions import MissingResource
from core.externals.mono.mono_client import MonoClient
from core.externals.schema import MonoTransactionSchema
from crud.account import CRUDAccount
from crud.category import CRUDCategory, CRUDUserCategory
from crud.currency import CRUDUserCurrency
from crud.rules import CRUDRules
from crud.transaction import CRUDTransaction
from models.account import Account
from models.category import Category, UserCategory
from models.currency import UserCurrency
from models.rules import TransactionRule
from models.transaction import Transaction
from schemas.account import MonoAccountCreate
from schemas.enums import AccountTypeEnum, MonoTransactionTypeEnum, TransactionTypeEnum
from schemas.transaction import MonoTransactionCreate, TransactionCreate
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
    ):
        self.crud_transaction = crud_transaction
        self.queue_connection = queue_connection
        self.crud_user_currency = crud_user_currency
        self.crud_account = crud_account
        self.crud_user_category = crud_user_category
        self.mono_client = mono_client
        self.crud_rules = crud_rules
        self.crud_category = crud_category

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
        user_currency, user_default_currency = await self.get_user_currency(
            user_id, data_obj.user_currency_id
        )
        data_obj.user_currency_id = user_currency.id

        data_obj.account_id = await self.validate_user_account(
            user_id=user_id, account_id=data_obj.account_id, is_paid=data_obj.is_paid
        )

        data_obj.amount_in_default = data_obj.amount / user_currency.exchange_rate
        data_obj.amount_in_default = to_minor_units(
            amount=data_obj.amount_in_default,
            currency=user_default_currency.currency.code,
        )
        data_obj.amount = to_minor_units(
            amount=data_obj.amount, currency=user_currency.currency.code
        )

        data_obj.user_id = user_id
        data_obj.date = (
            datetime.now(timezone.utc) if not data_obj.date else data_obj.date
        )
        category = await self.validate_user_category(user_id, data_obj.category_id)
        data_obj.category_id = category.category_id
        return self.crud_transaction.create(data_obj)

    async def list_user_transactions(self, user_id: int) -> List[Transaction]:
        transactions = self.crud_transaction.get_user_transactions_by_id(user_id)
        transactions = [convert_sql_models_to_dict(t) for t in transactions]

        new_transactions = []
        for trans in transactions:
            selected_currency, _ = await self.get_user_currency(
                user_id=user_id, user_currency_id=trans["user_currency_id"]
            )
            amount = Decimal(trans["amount_in_default"])
            rate = Decimal(str(selected_currency.exchange_rate))

            trans["amount_in_default"] = (amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            new_transactions.append(trans)
        return new_transactions

    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        transaction = self.crud_transaction.get_transaction_by_id(transaction_id)
        if transaction and transaction.user_id == user_id:
            return self.crud_transaction.delete(transaction_id)
        raise MissingResource(message="Transaction not found or access denied.")

    async def get_account_transactions(
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
        transaction = self.crud_transaction.get_transaction_by_id(transaction_id)
        if not transaction or transaction.user_id != user_id:
            raise MissingResource(message="Transaction not found or access denied.")
        return transaction

    async def get_user_currency(
        self, user_id: int, user_currency_id: int | None
    ) -> Tuple[UserCurrency, UserCurrency]:
        user_currencies = self.crud_user_currency.get_user_currencies(user_id)
        default_currency = sorted(
            user_currencies, key=lambda x: x.is_default, reverse=True
        )[0]
        selected_user_currency = None
        if not user_currency_id:
            selected_user_currency = default_currency
        elif user_currency_id not in [uc.id for uc in user_currencies]:
            selected_user_currency = default_currency
        else:
            selected_user_currency = next(
                (uc for uc in user_currencies if uc.id == user_currency_id), None
            )
        return selected_user_currency, default_currency

    async def validate_user_category(
        self, user_id: int, category_id: int | None
    ) -> UserCategory:
        user_categories = self.crud_user_category.get_user_categories(user_id)
        selected_category = None
        # TODO: Use default category if no user categories exist instead of the first one
        if category_id not in [cat.category_id for cat in user_categories]:
            selected_category = user_categories[0] if user_categories else None
        else:
            selected_category = next(
                (cat for cat in user_categories if cat.category_id == category_id), None
            )
        return selected_category

    async def validate_user_account(
        self,
        user_id: Column[int],
        account_id: int,
        is_paid: bool = True,
    ):
        user_accounts = self.crud_account.get_accounts(user_id)
        if not user_accounts:
            raise MissingResource(message="No accounts found for the user.")
        if account_id:
            if account_id not in [account.id for account in user_accounts]:
                account_id = None
        if not account_id:
            for account in user_accounts:
                if account.account_type == AccountTypeEnum.DEFAULT_PUBLIC:
                    account_id = account.id
                else:
                    account_id = account.id
        if not is_paid:
            for account in user_accounts:
                if account.account_type == AccountTypeEnum.DEFAULT_PRIVATE:
                    account_id = account.id

        return account_id

    async def create_mono_transactions(
        self,
        mono_account_id: str,
        user_id: int,
        account_id: int,
        start_date: date = None,
    ) -> None:
        user_currency, user_default_currency = await self.get_user_currency(
            user_id=user_id,
            user_currency_id=None,
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
