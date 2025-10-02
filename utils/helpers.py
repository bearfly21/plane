from passlib.hash import bcrypt
from decouple import config
import time
import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import  SessionLocal
from users.models import User, BlacklistedToken
from sqlalchemy.orm import selectinload


SECRET = config("SECRET")
ALGORITHM = config("ALGORITHM")


def hash_password(password):
    return bcrypt.hash(password)


def verify_password(password, hashed_password):
    return bcrypt.verify(password, hashed_password)


def is_authenticate(username):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return user
        return None
    finally:
        db.close()


def response_token(token:str):
    return{
        "access_token": token
    }
    
    
def generate_token(user_id:int):
    payload = {
        "user_id" : user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, key=SECRET, algorithm=ALGORITHM)
    return response_token(token)


def decode_jwt(token:str):
    payload = jwt.decode(token, key=SECRET, algorithms=[ALGORITHM])
    return payload if payload["expires"] >= time.time() else None


def is_token_bloked(token:str):
    db = SessionLocal()
    black_list_token = db.query(BlacklistedToken). filter(BlacklistedToken.token == token).first()
    if black_list_token:
        return True
    return False
        
        
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if is_token_bloked(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


def get_current_user(token:str = Depends(JWTBearer())):
    db = SessionLocal()
    pyload = decode_jwt(token)
    if pyload:
        user = db.query(User).filter(User.id == pyload["user_id"]).first()
        if user:
            return user
