from fastapi import APIRouter, Depends, Query, status
from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_planner_service
from models.user import User
from schemas.enums import PlannerTypeEnum
from schemas.planner import (
    PlannerAmountUpdate,
    PlannerCreate,
    PlannerCreateResponse,
    PlannerResponse,
    PlannerUpdate,
    PlannerWithTransactionsResponse,
)
from services import PlannerService


router = APIRouter(prefix="/planner", tags=["Planner"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PlannerCreateResponse,
)
async def create_planner(
    data: PlannerCreate,
    planner_service: PlannerService = Depends(get_planner_service),
    user: User = Depends(get_current_user),
):
    return await planner_service.create_planner(user_id=user.id, data_obj=data)


@router.get(
    "",
    response_model=list[PlannerResponse],
)
async def list_planners(
    user: User = Depends(get_current_user),
    type: PlannerTypeEnum | None = Query(None),
    planner_service: PlannerService = Depends(get_planner_service),
):
    return await planner_service.get_user_planners(user_id=user.id, type_query=type)


@router.get(
    "/{id}",
    response_model=PlannerWithTransactionsResponse,
)
async def get_planner(
    id: str,
    user: User = Depends(get_current_user),
    planner_service: PlannerService = Depends(get_planner_service),
):
    return await planner_service.get_single_planner(user_id=user.id, id=id)


@router.patch("/{id}/amount", response_model=PlannerResponse)
async def update_planner_amount(
    id: int,
    data: PlannerAmountUpdate,
    user: User = Depends(get_current_user),
    planner_service: PlannerService = Depends(get_planner_service),
):
    return await planner_service.update_planner_amount(
        user_id=user.id, id=id, data_obj=data
    )


@router.put("/{id}", response_model=PlannerResponse)
async def update_planner(
    id: int,
    data: PlannerUpdate,
    user: User = Depends(get_current_user),
    planner_service: PlannerService = Depends(get_planner_service),
):
    return await planner_service.update_planner(user_id=user.id, id=id, data_obj=data)
