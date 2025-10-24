from datetime import date
from core.externals.mono.mono_client import get_mono_client


# TODO: Rename this function
async def retrieve_user_mono_transactions(
    ctx,
    mono_account_id: str,
    user_id: int,
    account_id: int,
    start_date: date = None,
) -> None:
    from api.dependencies.service import get_transaction_service

    mono_client = get_mono_client()
    transaction_service = get_transaction_service(
        crud_transaction=ctx["crud_transaction"],
        crud_user_currency=ctx["crud_user_currency"],
        crud_account=ctx["crud_account"],
        crud_user_category=ctx["crud_user_category"],
        mono_client=mono_client,
        crud_rules=ctx["crud_rules"],
        crud_category=ctx["crud_category"],
    )
    # TODO: Handle deduplication of transactions here
    await transaction_service.create_mono_transactions(
        mono_account_id=mono_account_id,
        user_id=user_id,
        account_id=account_id,
        start_date=start_date,
    )
    return
