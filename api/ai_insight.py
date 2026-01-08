from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_ai_insight_service
from models.user import User
from schemas.ai_schemas import NlRequest, NlResponse
from services.ai_insight import AIInsightService

router = APIRouter(prefix="/insights", tags=["Insight"])


@router.post("/query", response_model=NlResponse)
async def query_insight(
    query: NlRequest,
    current_user: User = Depends(get_current_user),
    ai_insight_service: AIInsightService = Depends(get_ai_insight_service),
):
    stream = ai_insight_service.query_insight(
        query=query.query,
        user_id=current_user.id,
    )
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
    )
