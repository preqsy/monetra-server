import logging
from datetime import datetime, timedelta, timezone
from crud.account import CRUDAccount
from crud.user import CRUDAuthUser

logger = logging.getLogger(__name__)


async def update_user_last_activity(ctx, user_id: int):

    from task_queue.main import get_queue_connection

    crud_user: CRUDAuthUser = ctx["crud_user"]
    crud_account: CRUDAccount = ctx["crud_account"]
    queue_connection = await get_queue_connection()
    user = crud_user.get(id=user_id)
    user_automatic_accounts = crud_account.get_automatic_accounts(user_id=user_id)

    if not user_automatic_accounts:
        logger.info(f"No automatic accounts found for user {user_id}")
        return

    if user.last_activity_time and (
        datetime.now(timezone.utc) - user.last_activity_time
    ) > timedelta(days=1):

        for account in user_automatic_accounts:
            await queue_connection.enqueue_job(
                "retrieve_user_mono_transactions",
                user_id=user_id,
                mono_account_id=account.ext_account_id,
                account_id=account.id,
                start_date=datetime.now(timezone.utc),
            )

    crud_user.update(
        id=user_id, data_obj={"last_activity_time": datetime.now(timezone.utc)}
    )
    logger.info(f"Updated last activity time for user {user_id}")
    return
