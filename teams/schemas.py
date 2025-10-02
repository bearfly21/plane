from pydantic import BaseModel, EmailStr
from typing import Optional

class TeamCreateSchema(BaseModel):
    name: str
    project_id: int


class InviteMemberSchema(BaseModel):
    email:EmailStr

class AcceptInviteSchema(BaseModel):
    team_id: int


class AssignRoleSchema(BaseModel):
    membership_id: int
    role_id: int
