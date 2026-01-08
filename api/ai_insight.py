from fastapi import APIRouter, Depends, Query

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_ai_insight_service
from models.user import User
from schemas.ai_schemas import NlRequest
from services.ai_insight import AIInsightService

router = APIRouter(prefix="/insights", tags=["Insight"])


@router.post("/query")
async def query_insight(
    query: NlRequest,
    current_user: User = Depends(get_current_user),
    ai_insight_service: AIInsightService = Depends(get_ai_insight_service),
):
    return await ai_insight_service.query_insight(
        query=query.query,
        user_id=current_user.id,
    )
