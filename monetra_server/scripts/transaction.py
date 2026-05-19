import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import random

from tarsq import schedule, task

from monetra_server.core.externals.mono.mono_client import get_mono_client
from monetra_server.crud.account import CRUDAccount
from monetra_server.crud.category import (
    CRUDCategory,
    CRUDUserCategory,
)
from monetra_server.crud.currency import CRUDCurrency, CRUDUserCurrency
from monetra_server.crud.rules import CRUDRules
from monetra_server.crud.transaction import CRUDTransaction
from monetra_server.crud.user import CRUDAuthUser
from monetra_server.schemas.enums import AccountTypeEnum, TransactionTypeEnum
from monetra_server.schemas.transaction import TransactionCreate
from monetra_server.services.account import AccountService
from monetra_server.services.category import CategoryService
from monetra_server.services.currency import CurrencyService
from monetra_server.services.transaction import TransactionService

SAMPLE_TRANSACTIONS = [
    {
        "notes": "Grocery shopping",
        "transaction_type": TransactionTypeEnum.EXPENSE,
        "amount": 50,
    },
    {
        "notes": "Salary credit",
        "transaction_type": TransactionTypeEnum.INCOME,
        "amount": 2000,
    },
    {
        "notes": "Electricity bill",
        "transaction_type": TransactionTypeEnum.EXPENSE,
        "amount": 80,
    },
    {
        "notes": "Freelance payment",
        "transaction_type": TransactionTypeEnum.INCOME,
        "amount": 500,
    },
    {
        "notes": "Transport fare",
        "transaction_type": TransactionTypeEnum.EXPENSE,
        "amount": 15,
    },
    {
        "notes": "Restaurant dinner",
        "transaction_type": TransactionTypeEnum.EXPENSE,
        "amount": 120,
    },
    {
        "notes": "Interest earned",
        "transaction_type": TransactionTypeEnum.INCOME,
        "amount": 30,
    },
]


@schedule("create_sample_transactions", cron="every minute")
@task("create_sample_transactions", max_retries=2)
async def create_sample_transactions(ctx, payload: dict = None):
    crud_user: CRUDAuthUser = ctx["crud_user"]()
    crud_account: CRUDAccount = ctx["crud_account"]()
    crud_user_currency: CRUDUserCurrency = ctx["crud_user_currency"]()
    crud_currency: CRUDCurrency = ctx["crud_currency"]()
    crud_category: CRUDCategory = ctx["crud_category"]()
    crud_user_category: CRUDUserCategory = ctx["crud_user_category"]()
    crud_transaction: CRUDTransaction = ctx["crud_transaction"]()
    crud_rules: CRUDRules = ctx["crud_rules"]()

    user = crud_user.get_by_email(email="test@gmail.com")
    if not user:
        return

    print(f"Creating sample transaction for user: {user.name}")

    default_account = (
        crud_account._get_account_query_by_user_id(user.id)
        .filter(crud_account.model.account_type == AccountTypeEnum.DEFAULT_PUBLIC)
        .first()
    )
    if not default_account:
        return

    default_currency = crud_user_currency.get_user_default_currency(user.id)
    if not default_currency:
        return

    sample = random.choice(SAMPLE_TRANSACTIONS)
    income_cat, expense_cat = crud_category.get_uncategorized_income_and_expense()
    category_id = (
        income_cat.id
        if sample["transaction_type"] == TransactionTypeEnum.INCOME
        else expense_cat.id
    )

    transaction_service = TransactionService(
        crud_transaction=crud_transaction,
        crud_user_currency=crud_user_currency,
        crud_account=crud_account,
        crud_user_category=crud_user_category,
        mono_client=get_mono_client(),
        crud_rules=crud_rules,
        crud_category=crud_category,
        currency_service=CurrencyService(crud_currency, crud_user_currency),
        account_service=AccountService(crud_account, crud_currency, crud_user_currency),
        category_service=CategoryService(crud_category, crud_user_category),
    )

    trans = await transaction_service.create_transaction(
        data_obj=TransactionCreate(
            amount=sample["amount"],
            transaction_type=sample["transaction_type"],
            account_id=default_account.id,
            user_currency_id=default_currency.id,
            category_id=category_id,
            notes=sample["notes"],
        ),
        user_id=user.id,
    )
    print(f"Created transaction: {trans.id} ({sample['notes']}) for user: {user.name}")
