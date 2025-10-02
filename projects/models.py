from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from users.models import User
    from comments.models import Comment
    from tasks.models import Task
    from teams.models import Team


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="owned_projects")
    teams = relationship("Team", secondary="project_teams", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

