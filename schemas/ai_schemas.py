from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from schemas.enums import TransactionTypeEnum


IntentType = Literal["spent_total", "list_transaction", "unknown"]
TargetKind = Literal["category", "unknown"]


class NLParse(BaseModel):
    schema_version: Literal["v1"] = "v1"
    intent: IntentType
    target_kind: TargetKind
    target_text: str = Field(min_length=1, max_length=120)


class NLResolveRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=1, max_length=500)

    top_k: int = Field(default=25, ge=5, le=100)


class TransactionObj(BaseModel):
    doc_id: str
    transaction_type: TransactionTypeEnum
    amount: int
    currency: str
    account_id: int
    category: str
    date_utc: str


class ResolvedCategory(BaseModel):
    transaction_id: int
    category_id: int
    hit_score: float
    cat_sim: float
    category: str
    payload: TransactionObj


class DiscardedCategory(BaseModel):
    transaction_id: int
    category: str


class NLResolveResult(BaseModel):
    ok: bool
    parse: Optional[NLParse] = None

    resolved_category: Optional[str] = ""
    resolved_category_id: Optional[int] = None
    resolved_candidates: List[ResolvedCategory] = Field(default_factory=list)
    discarded_candidates: List[DiscardedCategory] = Field(default_factory=list)
    category_scores: Optional[list] = []


class NlRequest(BaseModel):
    query: str
    session_id: str


class NlResponse(BaseModel):
    message: str
