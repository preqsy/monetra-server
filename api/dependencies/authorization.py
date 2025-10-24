from datetime import datetime, timedelta, timezone
from arq import ArqRedis
from fastapi import Depends

from core.exceptions import InvalidRequest
from core.externals.firebase.auth_dep import verify_firebase_token
from crud.user import CRUDAuthUser, get_crud_auth_user
from task_queue.main import get_queue_connection
from models.user import User


async def get_current_user(
    user: dict = Depends(verify_firebase_token),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    queue_connection: ArqRedis = Depends(get_queue_connection),
) -> User:
    user_data = crud_auth_user.get_user_by_uid(user["uid"])
    if not user_data:
        raise InvalidRequest("User not found")

    if user_data.last_activity_time and datetime.now(
        timezone.utc
    ) - user_data.last_activity_time > timedelta(minutes=20):
        await queue_connection.enqueue_job(
            "update_user_last_activity", user_id=user_data.id
        )
    return user_data
