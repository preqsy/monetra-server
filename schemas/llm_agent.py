from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="The user's message to the AI agent")
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation continuity"
    )
    conversation_id: Optional[int] = Field(
        None, description="Specific conversation ID to continue"
    )


class ChatMessageResponse(BaseModel):
    conversation_id: int = Field(..., description="ID of the conversation")
    session_id: str = Field(..., description="Session ID of the conversation")
    response: str = Field(..., description="AI agent's response")
    timestamp: str = Field(..., description="Timestamp of the response")
    error: Optional[str] = Field(None, description="Error message if any")


class ConversationCreateRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the conversation")
    title: Optional[str] = Field(
        None, description="Optional title for the conversation"
    )


class ConversationResponse(BaseModel):
    id: int = Field(..., description="Conversation ID")
    session_id: str = Field(..., description="Session ID")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    message_count: int = Field(0, description="Number of messages in conversation")


class MessageResponse(BaseModel):
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Creation timestamp")


class ConversationHistoryResponse(BaseModel):
    conversation_id: int = Field(..., description="Conversation ID")
    messages: List[MessageResponse] = Field(
        ..., description="List of messages in the conversation"
    )


class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., description="New title for the conversation")


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse] = Field(
        ..., description="List of user conversations"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
