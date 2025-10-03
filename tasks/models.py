from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
import enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from projects.models import Project
    from users.models import User
    from comments.models import Comment
    from tasks.models import Task


class TaskStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus, native_enum=False), default=TaskStatus.new)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)

    author_id = Column(ForeignKey("users.id", ondelete="SET NULL"))
    assignee_id = Column(ForeignKey("users.id", ondelete="SET NULL"))
    project_id = Column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    author = relationship("User", foreign_keys=[author_id], back_populates="tasks_authored")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tasks_assigned")
    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")