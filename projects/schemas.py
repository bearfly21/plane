from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ProjectCreateSchema(BaseModel):
    name: str

class InviteMemberSchema(BaseModel):
    email:EmailStr

class AcceptInviteSchema(BaseModel):
    project_id: int


class AssignRoleSchema(BaseModel):
    project_id: int
    user_id: int
    role_id: int