from fastapi import APIRouter

from .auth import router as auth_router
from .account import router as account_router
from .currency import router as currency_router
from .transaction import router as transaction_router
from .category import router as category_router
from .external import router as plaid_router
from .config import router as config_router
from .planner import router as planner_router
from .rules import router as rules_router
from .subscription import router as subscription_router
from .summary import router as summary_router
from .llm_agent import router as llm_agent_router
from .budget import router as budget_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(account_router)
router.include_router(currency_router)
router.include_router(transaction_router)
router.include_router(category_router)
router.include_router(plaid_router)
router.include_router(config_router)
router.include_router(planner_router)
router.include_router(rules_router)
router.include_router(subscription_router)
router.include_router(summary_router)
router.include_router(llm_agent_router)
router.include_router(budget_router)


@router.on_event("startup")
async def startup_event():
    from crud.category import crud_category

    crud_category.add_default_categories()
