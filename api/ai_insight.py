from fastapi import APIRouter, Depends, Query

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_ai_insight_service
from models.user import User
from services.ai_insight import AIInsightService

router = APIRouter(prefix="/insights", tags=["Insight"])


@router.get("/query")
async def query_insight(
    query: str = Query(..., description="The insight query to be processed."),
    current_user: User = Depends(get_current_user),
    ai_insight_service: AIInsightService = Depends(get_ai_insight_service),
):
    return await ai_insight_service.query_insight(
        query=query,
        user_id=current_user.id,
    )
