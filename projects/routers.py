from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import ProjectSchema, ProjectOut, ProjectUpdateSchema
from core.database import get_db
from utils.helpers import get_current_user
from .models import Project
from teams.models import TeamMembership, Team
from teams.schemas import TeamMembershipOut, TeamOutSchema
from users.models import User
from roles.models import Role



project_route = APIRouter()



@project_route.post("/create-project", status_code=status.HTTP_201_CREATED)
async def create_project(data:ProjectSchema, db:Session = Depends(get_db), owner = Depends(get_current_user)):
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Naot authorized")
    project = Project(name = data.name, owner_id = owner.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"message": "Project created"}




@project_route.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_member = (
        db.query(TeamMembership)
        .join(Team)
        .filter(
            Team.id.in_([t.id for t in project.teams]),
            TeamMembership.user_id == current_user.id
        )
        .first()
    )
    if not is_member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    teams_out = []
    for team in project.teams:
        memberships_out = [
            TeamMembershipOut.from_orm_with_role(m)
            for m in team.memberships
            if m.status == "accepted"
        ]
        teams_out.append(TeamOutSchema(
            id=team.id,
            name=team.name,
            memberships=memberships_out
        ))

    return ProjectOut(
        id=project.id,
        name=project.name,
        owner=project.owner,
        teams=teams_out
    )




@project_route.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


    is_admin = (
        db.query(TeamMembership)
        .join(Role)
        .join(Team)
        .filter(
            Team.id.in_([t.id for t in project.teams]),
            TeamMembership.user_id == current_user.id,
            Role.name.in_(["admin", "owner"])
        )
        .first()
    )
    if not is_admin and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner or admin can update project")

    if data.name:
        project.name = data.name
    teams_out = []
    for team in project.teams:
        memberships_out = [
            TeamMembershipOut.from_orm_with_role(m)
            for m in team.memberships
            if m.status == "accepted"
        ]
        teams_out.append(TeamOutSchema(
            id=team.id,
            name=team.name,
            memberships=memberships_out
        ))

    db.commit()
    db.refresh(project)
    return ProjectOut(
        id=project.id,
        name=project.name,
        owner=project.owner,
        teams=teams_out

    )


@project_route.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only project owner can delete")

    db.delete(project)
    db.commit()
