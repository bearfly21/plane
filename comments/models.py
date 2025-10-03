from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    task_id = Column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")