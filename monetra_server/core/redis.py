import logfire
from redis import Redis
from core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    health_check_interval=30,
    decode_responses=True,
)


def get_redis_client() -> Redis:
    return redis_client


def init_redis_client() -> Redis:
    logfire.info("Initializing Redis client...")
    global redis_client
    return redis_client


def close_redis() -> None:
    logfire.info("Closing Redis client...")
    if redis_client:
        redis_client.close()
