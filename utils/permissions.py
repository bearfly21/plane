from roles.models import Permission
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from teams.models import TeamMembership
from roles.models import Role
from core.database import get_db
from .helpers import get_current_user


def add_permissions(models,session):
    permissions = []
    actions = ["add", "read", "update", "delete"]
    for model in models:
        for action in actions:
            permissions.append(
                {
                    "name": f"{action}_{model}",
                    "description": f"can {action} {model}"
                }
            )
    session.execute(Permission.__table__.insert(), permissions)  
    session.commit()



 

def require_team_role( allowed_roles: list[str]):
    def dependency(
        team_id:int,
        db: Session = Depends(get_db),
        user = Depends(get_current_user)
    ):
        membership = (
            db.query(TeamMembership)
            .join(Role)
            .filter(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == user.id,
                Role.name.in_(allowed_roles)
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission for this action"
            )
        return membership  
    return dependency
