from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
from tasks.models import Task
from comments.models import Comment
from activity_logs.models import ActivityLog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from projects.models import Project, project_users
    from comments.models import Comment
    from tasks.models import Task
    from activity_logs.models import ActivityLog
    


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owned_projects = relationship("Project", back_populates="owner")
    project_roles = relationship("ProjectUserRole", back_populates="user", cascade="all, delete-orphan")
    tasks_authored = relationship("Task", back_populates="author", foreign_keys="Task.author_id")
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="author")
    activities = relationship("ActivityLog", back_populates="user")



class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False)             
    created_at = Column(DateTime, default=datetime.utcnow)