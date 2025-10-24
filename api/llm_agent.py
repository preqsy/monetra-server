from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from core.config import settings
from models.user import User
from services.llm_agent import LLMAgentService
from api.dependencies.service import (
    get_crud_transaction,
    get_crud_account,
    get_crud_category,
    get_crud_user_category,
    get_crud_user_currency,
    get_crud_total_summary,
    get_crud_planner,
    get_transaction_service,
    get_account_service,
    get_account_summary_service,
)
from schemas.llm_agent import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreateRequest,
    ConversationResponse,
    ConversationHistoryResponse,
    ConversationUpdateRequest,
    ConversationListResponse,
    MessageResponse,
)
from api.dependencies.authorization import get_current_user

router = APIRouter(prefix="/llm-agent", tags=["LLM Agent"])


def get_llm_agent_service(
    db: Session = Depends(get_db),
    crud_transaction=Depends(get_crud_transaction),
    crud_account=Depends(get_crud_account),
    crud_category=Depends(get_crud_category),
    crud_user_category=Depends(get_crud_user_category),
    crud_user_currency=Depends(get_crud_user_currency),
    crud_total_summary=Depends(get_crud_total_summary),
    crud_planner=Depends(get_crud_planner),
    transaction_service=Depends(get_transaction_service),
    account_service=Depends(get_account_service),
    summary_service=Depends(get_account_summary_service),
) -> LLMAgentService:
    """Dependency to get LLM agent service"""
    return LLMAgentService(
        db_session=db,
        settings=settings,
        crud_transaction=crud_transaction,
        crud_account=crud_account,
        crud_category=crud_category,
        crud_user_category=crud_user_category,
        crud_user_currency=crud_user_currency,
        crud_total_summary=crud_total_summary,
        crud_planner=crud_planner,
        transaction_service=transaction_service,
        account_service=account_service,
        summary_service=summary_service,
    )


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_agent(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Send a message to the AI financial agent"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        result = await llm_service.process_chat_message(
            user_id=current_user.id,
            message=request.message,
            session_id=request.session_id,
            conversation_id=request.conversation_id,
        )
        return ChatMessageResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service temporarily unavailable: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Create a new conversation"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        result = llm_service.create_conversation(
            user_id=current_user.id, session_id=request.session_id, title=request.title
        )
        return ConversationResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}",
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_user_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Get all conversations for the current user"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        conversations_data = llm_service.get_user_conversations(
            user_id=current_user.id, limit=limit
        )
        conversations = [ConversationResponse(**conv) for conv in conversations_data]
        return ConversationListResponse(conversations=conversations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}/history",
    response_model=ConversationHistoryResponse,
)
async def get_conversation_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Get conversation history for a specific conversation"""
    if conversation_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID",
        )

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        messages_data = llm_service.get_conversation_history(
            conversation_id=conversation_id, user_id=current_user.id
        )
        messages = [MessageResponse(**msg) for msg in messages_data]
        return ConversationHistoryResponse(
            conversation_id=conversation_id, messages=messages
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation history: {str(e)}",
        )


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int,
    request: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Update conversation title"""
    if conversation_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID",
        )

    if not request.title or len(request.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        success = llm_service.update_conversation_title(
            conversation_id=conversation_id,
            user_id=current_user.id,
            title=request.title,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )
        return {"message": "Conversation title updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation title: {str(e)}",
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    llm_service: LLMAgentService = Depends(get_llm_agent_service),
):
    """Delete a conversation"""
    if conversation_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID",
        )

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found",
            )
        success = llm_service.delete_conversation(
            conversation_id=conversation_id, user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the LLM agent service"""
    return {"status": "healthy", "service": "llm-agent"}
