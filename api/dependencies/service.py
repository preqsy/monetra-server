from core.externals.mono.mono_client import get_mono_client
from core.externals.plaid.plaid_client import get_plaid_client
from crud.account import get_crud_account
from fastapi.params import Depends
from crud.budget import get_crud_budget
from crud.category import (
    get_crud_category,
    get_crud_user_category,
)
from crud.currency import (
    get_crud_currency,
    get_crud_user_currency,
)
from crud.planner import get_crud_planner
from crud.rules import get_crud_rules
from crud.subscription import get_crud_subscription_plan, get_crud_user_subscription
from crud.summary import get_crud_total_summary
from crud.transaction import get_crud_transaction
from crud.user import get_crud_auth_user
from services import (
    PlannerService,
    TransactionService,
    AccountService,
    AuthService,
    CategoryService,
    CurrencyService,
    ExternalService,
    TransactionRuleService,
    SubscriptionService,
    AccountSummaryService,
    BudgetService,
)

from task_queue.main import get_queue_connection


def get_transaction_service(
    crud_transaction=Depends(get_crud_transaction),
    queue_connection=Depends(get_queue_connection),
    crud_user_currency=Depends(get_crud_user_currency),
    crud_account=Depends(get_crud_account),
    crud_user_category=Depends(get_crud_user_category),
    crud_rules=Depends(get_crud_rules),
    crud_category=Depends(get_crud_category),
    mono_client=Depends(get_mono_client),
) -> TransactionService:
    return TransactionService(
        crud_transaction=crud_transaction,
        queue_connection=queue_connection,
        crud_user_currency=crud_user_currency,
        crud_account=crud_account,
        crud_user_category=crud_user_category,
        mono_client=mono_client,
        crud_rules=crud_rules,
        crud_category=crud_category,
    )


def get_account_service(
    crud_account=Depends(get_crud_account),
    crud_currency=Depends(get_crud_currency),
    crud_user_currency=Depends(get_crud_user_currency),
    transaction_service=Depends(get_transaction_service),
) -> AccountService:
    return AccountService(
        crud_account=crud_account,
        crud_currency=crud_currency,
        crud_user_currency=crud_user_currency,
        transaction_service=transaction_service,
    )


def get_auth_service(
    crud_auth_user=Depends(get_crud_auth_user),
    crud_account=Depends(get_crud_account),
    mono_client=Depends(get_mono_client),
    queue_connection=Depends(get_queue_connection),
    crud_currency=Depends(get_crud_currency),
    crud_user_currency=Depends(get_crud_user_currency),
) -> AuthService:
    return AuthService(
        crud_auth_user=crud_auth_user,
        crud_account=crud_account,
        mono_client=mono_client,
        queue_connection=queue_connection,
        crud_currency=crud_currency,
        crud_user_currency=crud_user_currency,
    )


def get_category_service(
    crud_category=Depends(get_crud_category),
    crud_user_category=Depends(get_crud_user_category),
):
    return CategoryService(crud_category, crud_user_category)


def get_currency_service(
    crud_currency=Depends(get_crud_currency),
    crud_user_currency=Depends(get_crud_user_currency),
    queue_connection=Depends(get_queue_connection),
) -> CurrencyService:
    return CurrencyService(crud_currency, crud_user_currency, queue_connection)


def get_external_service(
    plaid_client=Depends(get_plaid_client),
    mono_client=Depends(get_mono_client),
    crud_account=Depends(get_crud_account),
    queue_connection=Depends(get_queue_connection),
    crud_currency=Depends(get_crud_currency),
    crud_user_currency=Depends(get_crud_user_currency),
    crud_auth_user=Depends(get_crud_auth_user),
) -> ExternalService:
    return ExternalService(
        plaid_client=plaid_client,
        mono_client=mono_client,
        crud_account=crud_account,
        queue_connection=queue_connection,
        crud_currency=crud_currency,
        crud_user_currency=crud_user_currency,
        crud_user=crud_auth_user,
    )


def get_transaction_rule_service(
    crud_rules=Depends(get_crud_rules),
    crud_user_category=Depends(get_crud_user_category),
) -> TransactionRuleService:
    return TransactionRuleService(
        crud_rules=crud_rules,
        crud_user_category=crud_user_category,
    )


async def get_subscription_service(
    crud_user_subscription=Depends(get_crud_user_subscription),
    crud_subscription_plan=Depends(get_crud_subscription_plan),
) -> SubscriptionService:
    return SubscriptionService(
        crud_user_subscription=crud_user_subscription,
        crud_subscription_plan=crud_subscription_plan,
    )


def get_account_summary_service(
    crud_total_summary=Depends(get_crud_total_summary),
) -> AccountSummaryService:
    return AccountSummaryService(
        crud_total_summary=crud_total_summary,
    )


def get_budget_service(
    crud_budget=Depends(get_crud_budget),
    transaction_service=Depends(get_transaction_service),
) -> BudgetService:
    return BudgetService(
        crud_budget=crud_budget,
        transaction_service=transaction_service,
    )


def get_planner_service(
    crud_planner=Depends(get_crud_planner),
    crud_user_currency=Depends(get_crud_user_currency),
    crud_category=Depends(get_crud_category),
    crud_user_category=Depends(get_crud_user_category),
    transaction_service=Depends(get_transaction_service),
    category_service=Depends(get_category_service),
) -> PlannerService:
    return PlannerService(
        crud_planner=crud_planner,
        crud_user_currency=crud_user_currency,
        crud_category=crud_category,
        crud_user_category=crud_user_category,
        transaction_service=transaction_service,
        category_service=category_service,
    )
