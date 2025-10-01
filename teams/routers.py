from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from .shcemas import TeamCreateSchema
from .models import Team, TeamMembership
from utils.helpers import JWTBearer, get_current_user

team_route = APIRouter()

@team_route.post("/create_team", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def create_team(data:TeamCreateSchema, db:Session=Depends(get_db), owner = Depends(get_current_user)):
    if not owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not autorized")
    team = Team(name = data.name, owner_id = owner.id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@team_route.post("/add_member_to_team", status_code=status.HTTP_201_CREATED)
async def add_member_to_team(data)