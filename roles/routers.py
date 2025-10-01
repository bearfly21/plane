from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .shcemas import RoleCreateSchema
from core.database import get_db
from .models import Permission, Role
from teams.models import TeamMembership
from utils.helpers import JWTBearer

roles_and_permissions_route = APIRouter()

@roles_and_permissions_route.post("/create_role", dependencies=[Depends(JWTBearer)],status_code=status.HTTP_201_CREATED)
async def create_role(data:RoleCreateSchema, db:Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == data.name).first()
    if not role:
        role = Role(name = data.name)
    permissions = db.query(Permission).filter(Permission.id.in_(data.permissions)).all()
    role.permissions.extend(permissions)
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"message": "Role created"}


@roles_and_permissions_route.post("/add_role_to_member_of_team", status_code=status.HTTP_201_CREATED)
async def add_role_to_member_of_team(role_id:int, member_id:int, db:Session=Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    member = db.query(TeamMembership.user_id == member_id).first()
    if role and member:
        member.role == role
        db.add(member)
        db.commit()
        db.refresh(member)
        return {"message": "role added to member"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member or Role not found")