from fastapi import APIRouter, Depends, status

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_category_service
from models.user import User
from schemas.category import (
    CategoryCreate,
    CreateCategoryResponse,
    UserCategoryResponse,
    UserCategoryUpdate,
)
from services import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=CreateCategoryResponse
)
async def create_category(
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return await category_service.create_user_category(category, user.id)


@router.get(
    "",
    response_model=list[UserCategoryResponse],
)
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return await category_service.get_user_categories(user.id)


@router.put(
    "/{id}",
    response_model=UserCategoryResponse,
)
async def update_category(
    id: int,
    category: UserCategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return await category_service.update_user_category(
        user_id=user.id, data_obj=category, id=id
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int,
    category_service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return await category_service.delete_user_category(user_id=user.id, id=id)
