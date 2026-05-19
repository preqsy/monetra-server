from monetra_server.crud.account import get_crud_account
from monetra_server.crud.category import get_crud_category, get_crud_user_category
from monetra_server.crud.currency import get_crud_currency, get_crud_user_currency
from monetra_server.crud.rules import get_crud_rules
from monetra_server.crud.transaction import get_crud_transaction
from monetra_server.crud.user import get_crud_auth_user
from tarsq import WorkerSettings


def startup(ctx):
    ctx["crud_currency"] = get_crud_currency
    ctx["crud_user_currency"] = get_crud_user_currency
    ctx["crud_category"] = get_crud_category
    ctx["crud_user_category"] = get_crud_user_category
    ctx["crud_account"] = get_crud_account
    ctx["crud_transaction"] = get_crud_transaction
    ctx["crud_rules"] = get_crud_rules
    ctx["crud_user"] = get_crud_auth_user


class TarsqSettings(WorkerSettings):
    app: str = "monetra_server.task_queue.tasks"
    workers: int = 3
    timeout: int = 300
    on_startup = startup
    on_shutdown = None
