from crud.category import get_crud_category, get_crud_user_category
from crud.currency import get_crud_currency, get_crud_user_currency


class WorkerSettings:
    app: str = "task_queue.tasks.account"
    workers: int = 3
    timeout: int = 300
    ctx: dict = {
        "crud_currency": get_crud_currency(),
        "crud_user_currency": get_crud_user_currency(),
        "crud_category": get_crud_category(),
        "crud_user_category": get_crud_user_category(),
    }
    on_startup = None
    on_shutdown = None
