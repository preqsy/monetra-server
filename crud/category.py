from sqlalchemy.orm import joinedload

from core.db import get_db
from crud.base import CRUDBase
from models.category import Category, UserCategory
from schemas.category import DefaultCategoryCreate
from utils.helper import get_default_categories


class CRUDCategory(CRUDBase[Category]):

    def add_default_categories(self):
        default_categories = get_default_categories()
        for cat in default_categories:
            exist = self.db.query(Category).filter(Category.name == cat["name"]).first()
            if not exist:
                print("Adding default category: ", cat)
                data_obj = DefaultCategoryCreate(
                    name=cat["name"], type=cat["type"], is_default=True
                )
                self.create(data_obj)

    def get_uncategorized_income_and_expense(self) -> tuple[Category, Category]:
        return (
            self.db.query(Category)
            .filter(Category.name == "Uncategorized Income")
            .one(),
            self.db.query(Category)
            .filter(Category.name == "Uncategorized Expense")
            .one(),
        )

    def get_default_categories(self):
        return self.db.query(Category).filter(Category.is_default == True).all()


class CRUDUserCategory(CRUDBase[UserCategory]):
    def check_user_category_name_exists(self, user_id: int, name: str) -> bool:
        return (
            self.db.query(UserCategory)
            .filter(
                UserCategory.user_id == user_id, UserCategory.category.has(name=name)
            )
            .first()
            is not None
        )

    def get_user_categories(self, user_id: int) -> list[UserCategory]:
        return (
            self.db.query(UserCategory)
            .filter(UserCategory.user_id == user_id)
            .options(joinedload(UserCategory.category))
            .all()
        )

    def get_user_category(self, user_id: int, id: int) -> UserCategory | None:
        return (
            self.db.query(UserCategory)
            .filter(UserCategory.user_id == user_id, UserCategory.id == id)
            .options(joinedload(UserCategory.category))
            .first()
        )

    def get_user_category_by_category_id(self, user_id: int, category_id: int):
        return (
            self.db.query(UserCategory)
            .filter(
                UserCategory.user_id == user_id, UserCategory.category_id == category_id
            )
            .options(joinedload(UserCategory.category))
            .first()
        )


db_session = next(get_db())

crud_category = CRUDCategory(Category)


def get_crud_category():
    return crud_category


def get_crud_user_category():
    return CRUDUserCategory(model=UserCategory, db=db_session)
