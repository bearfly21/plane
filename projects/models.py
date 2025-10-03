from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
import enum
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from users.models import User
    from comments.models import Comment
    from tasks.models import Task


from sqlalchemy.orm import relationship

project_users = Table(
    "project_users",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="owned_projects")
    user_roles = relationship("ProjectUserRole", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project")


class MembershipStatus(str, enum.Enum):
    invited = "invited"
    accepted = "accepted"
    declined = "declined"
    removed = "removed"

class ProjectUserRole(Base):
    __tablename__ = "project_user_roles"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(MembershipStatus, native_enum=False), default=MembershipStatus.invited)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="project_roles")
    project = relationship("Project", back_populates="user_roles")
    role = relationship("Role")