from fastapi import APIRouter, Depends, HTTPException, status
from .shcemas import UserRegistrationSchema, UserLogoutSchema, UserLoginSchema, UserSchema
from sqlalchemy.orm import Session
from core.database import get_db
from utils.helpers import is_authenticate, hash_password, verify_password, JWTBearer, generate_token
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from users.models import User, BlacklistedToken


auth_router = APIRouter()

@auth_router.post("/register", response_model = UserSchema, status_code=status.HTTP_201_CREATED)
async def user_register(data: UserRegistrationSchema, db: Session = Depends(get_db)):
    user = is_authenticate(data.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    hashed_password = hash_password(data.password_hash)
    new_user = User(username=data.username, email = data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/login")
async def user_login(data:UserLoginSchema, db:Session=Depends(get_db)):
    user = is_authenticate(data.username)
    if not user or not verify_password(data.password_hash, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    return generate_token(user.id)


@auth_router.post("/logout", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def user_logout(token:str,db:Session = Depends(get_db)):
    blocked = BlacklistedToken(token=token)
    db.add(blocked)
    db.commit()
    db.refresh(blocked)
    return {"message":"logged out"}

