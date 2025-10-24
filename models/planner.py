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


class Planner(Base):
    __tablename__ = "planners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_currency_id = Column(
        Integer, ForeignKey("users_currencies.id"), nullable=False
    )
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    type = Column(String, nullable=False)
    name = Column(String, index=True, nullable=False)
    required_amount = Column(BigInteger, nullable=False)
    accumulated_amount = Column(BigInteger, nullable=False)
    required_amount_in_default = Column(BigInteger, nullable=False)
    accumulated_amount_in_default = Column(BigInteger, nullable=False)
    role = Column(String, nullable=True)
    note = Column(String)
    date = Column(Date, nullable=False)
    image = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )
    category = relationship("Category")
    user_currency = relationship("UserCurrency")
