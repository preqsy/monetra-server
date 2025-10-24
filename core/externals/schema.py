from typing import Optional, List

from pydantic import BaseModel, Field


class MonoTransactionSchema(BaseModel):
    """Schema for a mono transaction."""

    id: str
    narration: Optional[str] = None
    amount: Optional[int] = None
    type: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    balance: Optional[int] = None
    date: Optional[str] = None


class PlaidRequestTokenResponse(BaseModel):
    link_token: Optional[str] = None
    expiration: Optional[str] = None
    request_id: Optional[str] = None


class PlaidExchangeTokenResponse(BaseModel):
    access_token: str
    item_id: Optional[str] = None
    request_id: Optional[str] = None


class Balance(BaseModel):
    available: Optional[float] = Field(default=0.0)
    current: Optional[float] = Field(default=0.0)
    iso_currency_code: Optional[str] = Field(default="USD")
    limit: Optional[float] = Field(default=None)
    unofficial_currency_code: Optional[str] = Field(default=None)


class Account(BaseModel):
    account_id: Optional[str] = Field(default="")
    balances: Optional[Balance] = Field(default_factory=Balance)
    mask: Optional[str] = Field(default="")
    name: Optional[str] = Field(default="")
    official_name: Optional[str] = Field(default="")
    subtype: Optional[str] = Field(default="")
    type: Optional[str] = Field(default="")


class NumbersACH(BaseModel):
    account: Optional[str] = Field(default="")
    account_id: Optional[str] = Field(default="")
    routing: Optional[str] = Field(default="")
    wire_routing: Optional[str] = Field(default=None)


class Numbers(BaseModel):
    ach: Optional[List[NumbersACH]] = Field(default_factory=list)


class PlaidAccountResponse(BaseModel):
    accounts: Optional[List[Account]] = Field(default_factory=list)
    numbers: Optional[Numbers] = Field(default_factory=Numbers)
    request_id: Optional[str] = Field(default="")
