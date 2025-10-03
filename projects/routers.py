from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .schemas import ProjectCreateSchema, InviteMemberSchema, AcceptInviteSchema, AssignRoleSchema
from core.database import get_db
from utils.helpers import JWTBearer, get_current_user, generate_token
from utils.emails import send_invite_email
from .models import Project
from users.models import User
from roles.models import Role
from tasks.models import Task
from comments.models import Comment
from .models import ProjectUserRole, MembershipStatus


project_route = APIRouter()



@project_route.post("/create-project", status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreateSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = Project(name=data.name, owner_id=current_user.id)
    db.add(project)
    db.flush()

    owner_role = db.query(Role).filter_by(name="owner").first()
    db.add(ProjectUserRole(
        user_id=current_user.id,
        project_id=project.id,
        role_id=owner_role.id,
        status=MembershipStatus.accepted
    ))

    db.commit()
    db.refresh(project)
    return {"message": f"Project '{project.name}' created", "project_id": project.id}


@project_route.post("/projects/{project_id}/invite")
def invite_user(
    project_id: int,
    data: InviteMemberSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403)

    user = db.query(User).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404)

    existing = db.query(ProjectUserRole).filter_by(user_id=user.id, project_id=project_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already invited or joined")

    member_role = db.query(Role).filter_by(name="member").first()
    if not member_role:
        raise HTTPException(status_code=500, detail="Role 'member' not found")

    db.add(ProjectUserRole(
        user_id=user.id,
        project_id=project_id,
        role_id=member_role.id,
        status=MembershipStatus.invited
    ))

    invite_token = generate_token(user.id)
    background_tasks.add_task(send_invite_email, user.email, project.name, invite_token)

    db.commit()
    return {"message": f"Invitation sent to {user.email}"}




@project_route.post("/projects/accept-invite", status_code=status.HTTP_200_OK)
def accept_invite(data: AcceptInviteSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(ProjectUserRole).filter_by(user_id=current_user.id, project_id=data.project_id).first()
    if not membership or membership.status != MembershipStatus.invited:
        raise HTTPException(status_code=404)

    membership.status = MembershipStatus.accepted
    db.commit()
    return {"message": f"You've joined project {membership.project.name}"}



@project_route.post("/projects/assign-role")
def assign_role(data: AssignRoleSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter_by(id=data.project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403)

    membership = db.query(ProjectUserRole).filter_by(user_id=data.user_id, project_id=data.project_id).first()
    if not membership:
        raise HTTPException(status_code=404)

    role = db.query(Role).filter_by(id=data.role_id).first()
    if not role:
        raise HTTPException(status_code=404)

    membership.role_id = role.id
    db.commit()
    return {"message": f"Role '{role.name}' assigned to user {membership.user.email}"}



@project_route.delete("/projects/{project_id}/remove-user/{user_id}")
def remove_user(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403)

    membership = db.query(ProjectUserRole).filter_by(user_id=user_id, project_id=project_id).first()
    if not membership:
        raise HTTPException(status_code=404)

    db.delete(membership)
    db.commit()
    return {"message": "User removed from project"}


@project_route.get("/projects/{project_id}")
def get_project_details(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Проверка доступа: участник или владелец
    membership = db.query(ProjectUserRole).filter_by(
        user_id=current_user.id,
        project_id=project_id,
        status=MembershipStatus.accepted
    ).first()

    if not membership and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Участники
    members = (
        db.query(User, Role.name.label("role"))
        .join(ProjectUserRole, ProjectUserRole.user_id == User.id)
        .join(Role, Role.id == ProjectUserRole.role_id)
        .filter(ProjectUserRole.project_id == project_id, ProjectUserRole.status == MembershipStatus.accepted)
        .all()
    )

    # Задачи и комментарии
    tasks = db.query(Task).filter_by(project_id=project_id, is_deleted=False).all()
    task_data = []
    for task in tasks:
        comments = db.query(Comment).filter_by(task_id=task.id, is_deleted=False).all()
        task_data.append({
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "comments": [{"id": c.id, "text": c.text, "author": c.author.username} for c in comments]
        })

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "owner": project.owner.username
        },
        "members": [
            {"id": user.id, "username": user.username, "role": role}
            for user, role in members
        ],
        "tasks": task_data
    }


@project_route.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can delete this project")

    db.delete(project)
    db.commit()
    return {"message": f"Project '{project.name}' deleted"}
