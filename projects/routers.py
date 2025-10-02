from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import ProjectSchema
from core.database import get_db
from utils.helpers import get_current_user
from .models import Project

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

