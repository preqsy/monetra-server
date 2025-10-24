from sqlalchemy import Column, String, Integer, Numeric, Date, BigInteger
from sqlalchemy.orm import declarative_base
from core.db import Base


class AccountSummary(Base):
    __tablename__ = "account_summary"
    __table_args__ = {"extend_existing": True}

    account_id = Column(Integer, primary_key=True)
    account_name = Column(String)
    opening_balance = Column(Numeric)
    total_income = Column(Numeric)
    total_expense = Column(Numeric)
    current_balance = Column(Numeric)


class TotalSummary(Base):
    __tablename__ = "total_summary"
    __table_args__ = {"extend_existing": True}

    total_income = Column(BigInteger, primary_key=True)
    total_expense = Column(BigInteger)
    net_total = Column(BigInteger)
    total_cash_at_hand = Column(BigInteger)
    total_balance = Column(BigInteger)
    user_id = Column(Integer)
    default_user_currency_id = Column(Integer)
    default_currency_code = Column(String)
    month = Column(Integer)
    year = Column(Integer)
