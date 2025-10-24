from typing import Optional
from pydantic import BaseModel

from schemas.base import ReturnBaseModel
from schemas.enums import CategoryTypeEnum


class CategoryBase(BaseModel):
    name: str
    type: CategoryTypeEnum
    description: Optional[str] = None


class UserCategoryCreate(BaseModel):
    user_id: Optional[int] = None
    category_id: Optional[int] = None


class DefaultCategoryCreate(CategoryBase):
    is_default: Optional[bool] = True


class CategoryCreate(CategoryBase):
    pass


class CreateCategoryResponse(ReturnBaseModel, CategoryBase):
    pass


class UserCategoryResponse(ReturnBaseModel, UserCategoryCreate):
    category: CreateCategoryResponse


class UserCategoryUpdate(CategoryCreate):
    pass
