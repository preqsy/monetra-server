from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship
from core.db import Base


class TransactionRule(Base):
    __tablename__ = "transaction_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )
    beneficiary_name = Column(String, index=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )
    category = relationship("Category")
    user = relationship("User")
