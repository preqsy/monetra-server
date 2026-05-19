from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    String,
    Integer,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship
from core.db import Base


# TODO: CONSIDER ADD MONO CUSTOMER ID HERE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    mono_customer_id = Column(String, nullable=True)
    last_activity_time = Column(
        TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()")
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    # relationship to subscription
    subscriptions = relationship(
        "UserSubscription",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    currencies = relationship("UserCurrency", back_populates="user")
    categories = relationship("UserCategory", back_populates="user")


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(BigInteger, nullable=False, default=0.0)
    billing_cycle = Column(String, nullable=True)
    description = Column(String, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    # relationship to features
    features = relationship("PlanFeature", back_populates="plan")


class PlanFeature(Base):
    __tablename__ = "plan_features"

    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)

    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))
    plan = relationship("SubscriptionPlan", back_populates="features")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan")
