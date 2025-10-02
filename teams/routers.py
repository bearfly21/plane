from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from .schemas import TeamCreateSchema, InviteMemberSchema, AcceptInviteSchema, AssignRoleSchema
from .models import Team, TeamMembership
from utils.helpers import JWTBearer, get_current_user, generate_token
from utils.emails import send_invite_email
from teams.models import Team, TeamMembership, MembershipStatus
from users.models import User
from projects.models import Project
from roles.models import Role




team_route = APIRouter()

@team_route.post("/teams/create", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def create_team(data: TeamCreateSchema, db: Session = Depends(get_db), owner: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this project")

    team = Team(name=data.name)
    db.add(team)
    db.commit()
    db.refresh(team)

    project.teams.append(team)
    db.commit()

    return {"message": f"Team '{team.name}' created in project '{project.name}'", "team_id": team.id}


@team_route.post("/projects/{project_id}/teams/{team_id}/invite", status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int,
    team_id: int,
    data: InviteMemberSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only project owner can invite members")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")


    existing = db.query(TeamMembership).filter_by(user_id=user.id, team_id=team_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")

    membership = TeamMembership(
        user_id=user.id,
        team_id=team_id,
        status=MembershipStatus.pending
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    invite_token = generate_token(user.id)  
    background_tasks.add_task(send_invite_email, user.email, team.name, invite_token)


    return {
        "message": f"Invitation sent to {user.email}",
        "membership_id": membership.id
    }


@team_route.post("/teams/accept-invite", status_code=status.HTTP_200_OK)
def accept_invite(data: AcceptInviteSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(TeamMembership).filter_by(user_id=current_user.id, team_id=data.team_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="No invitation found")
    if membership.status != MembershipStatus.pending:
        raise HTTPException(status_code=400, detail="Invitation already accepted or invalid")

    membership.status = MembershipStatus.accepted
    db.commit()
    db.refresh(membership)
    return {"message": f"You've joined team {membership.team.name}"}


@team_route.post("/teams/assign-role", status_code=200)
def assign_role(data: AssignRoleSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(TeamMembership).filter_by(id=data.membership_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    team = membership.team
    project = db.query(Project).filter(Project.teams.contains(team)).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only project owner can assign roles")

    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    membership.role_id = role.id
    db.commit()
    db.refresh(membership)
    return {"message": f"Role '{role.name}' assigned to user {membership.user.email}"}


@team_route.delete("/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(
    membership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(TeamMembership).filter_by(id=membership_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    db.delete(membership)
    db.commit()

