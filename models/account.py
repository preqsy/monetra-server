from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    BigInteger,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship

from core.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    user_currency_id: Column[int] = Column(
        ForeignKey("users_currencies.id", onupdate="CASCADE"), nullable=False
    )
    amount = Column(BigInteger, nullable=False, default=0)  # Original Amount
    amount_in_default = Column(
        BigInteger, nullable=False, default=0
    )  # Amount in base currency
    account_type = Column(String, nullable=False)  # AUTOMATIC(MONO), MANUAL
    account_category = Column(String, nullable=False)  # e.g., CREDIT, BALANCE
    account_method = Column(
        String, nullable=True
    )  # e.g., CASH, VISA, MASTERCARD, CRYPTO

    account_number = Column(String, nullable=True)
    account_provider = Column(String, nullable=True)
    plaid_access_token = Column(String, nullable=True, unique=True)
    notes = Column(String, nullable=True)

    ext_account_id = Column(String, nullable=True)
    credit_amount = Column(BigInteger, nullable=True, default=0)
    last_sync_date = Column(TIMESTAMP(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=True, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    user_currency = relationship("UserCurrency")
