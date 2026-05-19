from fastapi import Depends, APIRouter, Query, status

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_budget_service
from schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetWithAmountResponse,
    TotalBudgetCreate,
    TotalBudgetResponse,
)

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BudgetResponse)
async def create_budget(
    data_obj: BudgetCreate,
    current_user=Depends(get_current_user),
    budget_service=Depends(get_budget_service),
):
    return await budget_service.create_budget(
        data_obj=data_obj, user_id=current_user.id
    )


@router.get(
    "",
    response_model=list[BudgetWithAmountResponse],
)
async def retrieve_budgets(
    period: str = Query(
        default="", description="Type of budget: DAILY, WEEKLY, MONTHLY"
    ),
    current_user=Depends(get_current_user),
    budget_service=Depends(get_budget_service),
):
    return await budget_service.calculate_budget(user_id=current_user.id, period=period)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_budget(
    budget_id: int,
    current_user=Depends(get_current_user),
    budget_service=Depends(get_budget_service),
):
    return await budget_service.delete_budget(
        budget_id=budget_id, user_id=current_user.id
    )


@router.get(
    "/total",
    response_model=TotalBudgetResponse,
)
async def get_total_budget(
    period: str = Query(
        default="", description="Type of budget: DAILY, WEEKLY, MONTHLY"
    ),
    current_user=Depends(get_current_user),
    budget_service=Depends(get_budget_service),
):
    return await budget_service.get_total_budget(user_id=current_user.id, period=period)


@router.post(
    "/total",
    response_model=BudgetResponse,
)
async def create_total_budget(
    data_obj: TotalBudgetCreate,
    current_user=Depends(get_current_user),
    budget_service=Depends(get_budget_service),
):
    return await budget_service.create_total_budget(
        user_id=current_user.id, data_obj=data_obj
    )
