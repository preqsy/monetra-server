from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, text
from core.db import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id = Column(String, index=True, nullable=False)

    role = Column(String, nullable=False)  # system | user | assistant
    content = Column(String, nullable=False)

    llm_model = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=text("now()"),
    )


class Session(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id = Column(String, unique=True, index=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
