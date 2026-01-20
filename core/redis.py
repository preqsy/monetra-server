import logfire
from redis import Redis

redis_client = Redis(
    host="localhost",
    port=6380,
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
