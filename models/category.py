from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String, Integer, text
from sqlalchemy.orm import relationship
from core.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    user_category = relationship("UserCategory", back_populates="category")


class UserCategory(Base):
    __tablename__ = "users_categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id: Column[int] = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    category_id: Column[int] = Column(
        ForeignKey("categories.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=text("now()"))

    category = relationship("Category", back_populates="user_category")
    user = relationship(
        "User",
        back_populates="categories",
    )
