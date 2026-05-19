from datetime import date
from typing import ClassVar
from pydantic import BaseModel, Field, model_validator

from schemas.enums import TransactionTypeEnum


class TransactionDoc(BaseModel):
    doc_id: int
    doc_type: str = Field(default="transaction")
    # text: str
    user_id: int
    transaction_id: int
    transaction_type: TransactionTypeEnum
    account_id: int
    category_id: int
    category: str
    currency: str
    amount: int
    date_utc: str = date.today().isoformat().replace("+00:00", "Z")
