from core.db import get_db
from crud.base import CRUDBase
from models.chat import ChatMessage
from schemas.chat import ChatMessageCreate


class CRUDChat(CRUDBase[ChatMessage,]):
    pass


db_session = next(get_db())


def get_crud_chat() -> CRUDChat:
    return CRUDChat(ChatMessage, db=db_session)
