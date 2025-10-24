from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import relationship

from core.db import Base


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=True)
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
    user_currencies = relationship("UserCurrency", back_populates="currency")

    def __repr__(self):
        return f"<Currency(code={self.code}, name={self.name}, symbol={self.symbol})>"


class UserCurrency(Base):
    __tablename__ = "users_currencies"

    id = Column(Integer, primary_key=True, index=True)
    user_id: Column[int] = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    currency_id: Column[int] = Column(
        ForeignKey("currencies.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    exchange_rate = Column(Numeric(precision=10, scale=4), nullable=False)
    is_default = Column(Boolean, default=False)
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
    currency = relationship("Currency", back_populates="user_currencies")
    user = relationship("User", back_populates="currencies")
