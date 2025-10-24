from datetime import date
from fastapi import Depends, APIRouter, Query
from api.dependencies.authorization import get_current_user
from models.user import User
from schemas.summary import SummaryResponse
from services import AccountSummaryService
from api.dependencies.service import get_account_summary_service


router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("", response_model=SummaryResponse)
def get_account_summary(
    date: date = Query(
        date.today(), description="Date to filter the summary by (YYYY-MM-DD)"
    ),
    account_summary_service: AccountSummaryService = Depends(
        get_account_summary_service
    ),
    user: User = Depends(get_current_user),
):
    return account_summary_service.get_account_summary(user_id=user.id, date=date)
