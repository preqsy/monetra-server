from datetime import date
from fastapi import Depends, APIRouter, Query
from monetra_server.api.dependencies.authorization import get_current_user
from monetra_server.models.user import User
from monetra_server.schemas.summary import SummaryResponse
from monetra_server.services import AccountSummaryService
from monetra_server.api.dependencies.service import get_account_summary_service


router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get(
    "",
    # response_model=SummaryResponse,
)
async def get_account_summary(
    date: date = Query(
        date.today(), description="Date to filter the summary by (YYYY-MM-DD)"
    ),
    account_summary_service: AccountSummaryService = Depends(
        get_account_summary_service
    ),
    user: User = Depends(get_current_user),
):
    return await account_summary_service.get_account_summary(user_id=user.id, date=date)
