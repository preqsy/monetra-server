import logging

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

from core import settings
from crud.category import get_crud_category, get_crud_user_category
from crud.rules import get_crud_rules
from crud.transaction import get_crud_transaction
from crud.user import get_crud_auth_user
from .tasks import registered_tasks

from crud.account import get_crud_account
from crud.currency import get_crud_currency, get_crud_user_currency


logging.basicConfig(level=logging.INFO)

REDIS_SETTINGS = RedisSettings(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
)


async def get_queue_connection() -> ArqRedis:
    return await create_pool(REDIS_SETTINGS)


async def startup(ctx):
    logging.info(
        f"Starting Redis connection pool {settings.REDIS_HOST}:{settings.REDIS_PORT}",
    )
    ctx["session"] = await get_queue_connection()
    ctx["crud_account"] = get_crud_account()
    ctx["crud_currency"] = get_crud_currency()
    ctx["crud_user_currency"] = get_crud_user_currency()
    ctx["crud_transaction"] = get_crud_transaction()
    ctx["crud_category"] = get_crud_category()
    ctx["crud_user_category"] = get_crud_user_category()
    ctx["crud_rules"] = get_crud_rules()
    ctx["crud_user"] = get_crud_auth_user()


async def shutdown(ctx):
    await ctx["session"]


class WorkerSettings:
    on_startup = startup
    redis_settings = REDIS_SETTINGS
    functions = registered_tasks
