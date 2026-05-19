from typing import Optional
from pydantic import BaseModel

from schemas.base import ReturnBaseModel


class RuleCreate(BaseModel):
    category_id: int
    beneficiary_name: str
    user_id: Optional[int] = None


class RuleResponse(RuleCreate, ReturnBaseModel):
    pass
