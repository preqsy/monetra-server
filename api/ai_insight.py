from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from api.dependencies.authorization import get_current_user
from api.dependencies.service import get_ai_insight_service
from core.exceptions import MissingResource
from models.user import User
from schemas.ai_schemas import NlRequest, NlResponse
from schemas.chat import SessionChatResponse
from services.ai_insight import AIInsightService

router = APIRouter(prefix="/insights", tags=["Insight"])


@router.post("/query", response_model=NlResponse)
async def query_insight(
    query: NlRequest,
    current_user: User = Depends(get_current_user),
    ai_insight_service: AIInsightService = Depends(get_ai_insight_service),
):
    if not ai_insight_service.crud_session.get_session_by_session_id(
        session_id=query.session_id, user_id=current_user.id
    ):
        raise MissingResource(message="Session ID not found")

    stream = ai_insight_service.query_insight(
        query=query.query,
        user_id=current_user.id,
        session_id=query.session_id,
    )
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
    )


@router.post("/create-session", response_model=SessionChatResponse)
async def create_session(
    current_user: User = Depends(get_current_user),
    ai_insight_service: AIInsightService = Depends(get_ai_insight_service),
):
    session_id = await ai_insight_service.create_session(user_id=current_user.id)
    return session_id
