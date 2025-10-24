from typing import Any

from models.conversation import Conversation, ConversationMessage
from utils.datetime_helper import get_utc_now


class ConversationManager:
    """Manages conversation history and context"""

    def __init__(self, db_session):
        self.db = db_session

    def create_conversation(
        self, user_id: int, session_id: str, title: str | None = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            title=title,
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> Conversation | None:
        """Get a conversation by ID for a specific user"""
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

    def get_conversation_by_session(
        self, session_id: str, user_id: int
    ) -> Conversation | None:
        """Get a conversation by session ID for a specific user"""
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

    def get_user_conversations(
        self, user_id: int, limit: int = 20
    ) -> list[Conversation]:
        """Get recent conversations for a user"""
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: dict[str, Any] | None = None,
        tool_results: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """Add a message to a conversation"""
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=str(tool_calls) if tool_calls else None,
            tool_results=str(tool_results) if tool_results else None,
        )
        self.db.add(message)

        # Update conversation timestamp
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conversation:
            conversation.updated_at = get_utc_now()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_conversation_messages(
        self, conversation_id: int, limit: int = 50
    ) -> list[ConversationMessage]:
        """Get messages for a conversation"""
        return (
            self.db.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def get_conversation_context(
        self, conversation_id: int, max_messages: int = 10
    ) -> list[dict[str, str | None]]:
        """Get conversation context for LLM"""
        messages = self.get_conversation_messages(conversation_id, max_messages)

        context = []
        for message in messages:
            context.append({"role": message.role, "content": message.content})

        return context

    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update conversation title"""
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conversation:
            conversation.title = title
            conversation.updated_at = get_utc_now()
            self.db.commit()
            return True
        return False

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and all its messages"""
        conversation = self.get_conversation(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False
