from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from utils.datetime_helper import get_utc_now

from core.db import Base


class Conversation(Base):
    """Database model for storing conversation history"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_utc_now)
    updated_at = Column(DateTime, nullable=True, onupdate=get_utc_now)

    # Relationship to messages
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    """Database model for storing individual messages in conversations"""

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=False, index=True
    )
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON string of tool calls made
    tool_results = Column(Text, nullable=True)  # JSON string of tool results
    created_at = Column(DateTime, nullable=False, default=get_utc_now)

    # Relationship to conversation
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
