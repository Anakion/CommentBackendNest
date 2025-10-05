from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="comments")

    # Иерархическая связь
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side=[id],
        backref="replies",
        cascade="all, delete-orphan"
    )
