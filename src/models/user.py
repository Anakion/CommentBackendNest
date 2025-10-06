from typing import Optional, List

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    homepage: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user")
