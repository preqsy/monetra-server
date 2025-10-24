from sqlalchemy import Column
from core.exceptions import MissingResource, ResourceExists
from crud.category import (
    CRUDCategory,
    CRUDUserCategory,
)
from schemas.category import CategoryCreate, UserCategoryCreate, UserCategoryUpdate


class CategoryService:
    def __init__(
        self, crud_category: CRUDCategory, crud_user_category: CRUDUserCategory
    ):
        self.crud_category = crud_category
        self.crud_user_category = crud_user_category

    async def create_user_category(
        self, data_obj: CategoryCreate, user_id: Column[int]
    ):
        data_obj.name = data_obj.name.title()
        if self.crud_user_category.check_user_category_name_exists(
            user_id, data_obj.name
        ):
            raise ResourceExists(
                message="Category with this name already exists for the user"
            )

        new_category = self.crud_category.create(data_obj)
        user_category_data = UserCategoryCreate(
            user_id=user_id, category_id=new_category.id
        )
        self.crud_user_category.create(user_category_data)

        return new_category

    async def get_user_categories(self, user_id: int):
        return self.crud_user_category.get_user_categories(user_id)

    async def update_user_category(
        self,
        *,
        user_id: int,
        data_obj: UserCategoryUpdate,
        id: int,
    ):
        category = self.crud_user_category.get_user_category(user_id, id)
        if not category:
            raise MissingResource(message="User category not found")

        data_obj.name = data_obj.name.title()
        updated_category = self.crud_category.update(
            id=category.category_id, data_obj=data_obj
        )
        self.crud_user_category.update(
            id=id,
            data_obj={"user_id": user_id, "category_id": updated_category.id},
        )
        return category

    async def delete_user_category(self, *, user_id: int, id: int):
        category = self.crud_user_category.get_user_category(user_id, id)
        if not category:
            raise MissingResource(message="User category not found")

        self.crud_category.delete(category.category_id)
        self.crud_user_category.delete(id)
        return None
