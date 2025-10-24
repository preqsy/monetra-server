from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from core.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    narration = Column(String, nullable=True)
    amount = Column(BigInteger, nullable=False, default=0)
    amount_in_default = Column(BigInteger, nullable=True, default=0)
    transaction_type = Column(String, nullable=False)
    mono_type = Column(String, nullable=True)
    mono_transaction_id = Column(String, nullable=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_currency_id = Column(
        Integer, ForeignKey("users_currencies.id"), nullable=False
    )
    balance = Column(Integer, nullable=True, default=0)
    date = Column(DateTime, nullable=False)
    is_paid = Column(Boolean, nullable=False, default=True)
    # OPTIONALS
    notes = Column(String, nullable=True)
    repeat = Column(String, nullable=True)
    remind = Column(String, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=text("now()"),
    )
    category = relationship("Category")
    user_currency = relationship("UserCurrency")
    account = relationship("Account")
