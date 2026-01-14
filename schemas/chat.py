from pydantic import BaseModel
from schemas.enums import ChatRoleEnum


class ChatMessageCreate(BaseModel):
    user_id: int
    role: ChatRoleEnum
    content: str
    session_id: str | None = None
    llm_model: str | None = None
