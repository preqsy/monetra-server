from crud.account import get_crud_account
from crud.category import get_crud_category, get_crud_user_category
from crud.currency import get_crud_currency, get_crud_user_currency
from crud.rules import get_crud_rules
from crud.transaction import get_crud_transaction
from crud.user import get_crud_auth_user


class WorkerSettings:
    app: str = "task_queue.tasks.account"
    workers: int = 3
    timeout: int = 300
    ctx: dict = {
        "crud_currency": get_crud_currency(),
        "crud_user_currency": get_crud_user_currency(),
        "crud_category": get_crud_category(),
        "crud_user_category": get_crud_user_category(),
        "crud_account": get_crud_account(),
        "crud_transaction": get_crud_transaction(),
        "crud_rules": get_crud_rules(),
        "crud_user": get_crud_auth_user(),
    }
    on_startup = None
    on_shutdown = None
