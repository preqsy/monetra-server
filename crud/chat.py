from core.db import get_db
from crud.base import CRUDBase
from models.chat import ChatMessage, Session
from schemas.chat import ChatMessageCreate


class CRUDChat(CRUDBase[ChatMessage,]):
    def get_messages_by_user_id(self, user_id: int):
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        return messages

    def get_messages_by_user_id_and_session_id(self, user_id: int, session_id: str):
        messages = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id, ChatMessage.session_id == session_id
            )
            .order_by(ChatMessage.created_at.asc())
            .limit(6)
            .all()
        )

        return messages


class CRUDSession(CRUDBase[Session]):
    def get_session_by_session_id(self, session_id: str, user_id: int):
        session = (
            self.db.query(Session)
            .filter(Session.session_id == session_id, Session.user_id == user_id)
            .first()
        )

        return session


db_session = next(get_db())


def get_crud_chat() -> CRUDChat:
    return CRUDChat(ChatMessage, db=db_session)


def get_crud_session() -> CRUDSession:
    return CRUDSession(Session, db=db_session)
