from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from core.database import Base
import enum
from projects.models import Project

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from users.models import User
    from roles.models import Role

# Many-to-Many Team ↔ Project
project_teams = Table(
    "project_teams",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    memberships = relationship("TeamMembership", back_populates="team")
    projects = relationship(Project, secondary=project_teams, back_populates="teams")
    tasks = relationship("Task", back_populates="team")

    

class MembershipStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"

class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.pending)

    user = relationship("User", back_populates="memberships")
    team = relationship("Team", back_populates="memberships")
    role = relationship("Role", back_populates="memberships")
