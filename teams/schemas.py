from pydantic import BaseModel, EmailStr
from typing import Optional, List
from users.shcemas import UserOutSchema



class TeamCreateSchema(BaseModel):
    name: str
    project_id: int

class TeamUpdateschema(BaseModel):
    name:str

class TeamOutSchema(BaseModel):
    id: int
    name: str
    memberships: List["TeamMembershipOut"]

    class Config:
        from_attributes = True



class InviteMemberSchema(BaseModel):
    email:EmailStr

class AcceptInviteSchema(BaseModel):
    team_id: int




class AssignRoleSchema(BaseModel):
    membership_id: int
    role_id: int
    team_id:int


class TeamMembershipOut(BaseModel):
    id: int
    user: UserOutSchema
    role: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

    
    @staticmethod
    def from_orm_with_role(membership):
        return TeamMembershipOut.model_validate({
            "id": membership.id,
            "user": UserOutSchema.model_validate(membership.user),
            "role": membership.role.name if membership.role else None,
            "status": membership.status
            })


