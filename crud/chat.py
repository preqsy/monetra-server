from core.db import get_db
from crud.base import CRUDBase
from models.chat import ChatMessage, Session
from schemas.chat import ChatMessageCreate


class CRUDChat(CRUDBase[ChatMessage,]):
    pass


class CRUDSession(CRUDBase[Session]):
    pass

db_session = next(get_db())

def get_crud_chat() -> CRUDChat:
    return CRUDChat(ChatMessage, db=db_session)

def get_crud_session() -> CRUDSession:
    return CRUDSession(Session, db=db_session)
