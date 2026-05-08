from tarsq import task

from crud.category import CRUDCategory, CRUDUserCategory


@task("add_user_default_categories")
async def add_user_default_categories(ctx, user_id: dict | int):
    user_id = user_id.get("user_id") if isinstance(user_id, dict) else user_id
    crud_category: CRUDCategory = ctx["crud_category"]
    crud_user_category: CRUDUserCategory = ctx["crud_user_category"]

    default_categories = crud_category.get_default_categories()
    user_default_categories = [
        {"user_id": user_id, "category_id": cat.id} for cat in default_categories
    ]
    crud_user_category.bulk_insert(user_default_categories)
