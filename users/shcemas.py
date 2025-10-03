from pydantic import BaseModel, EmailStr, model_validator, field_validator
from datetime import datetime


class UserRegistrationSchema(BaseModel):
    username: str   
    email: EmailStr
    password_hash: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password_hash != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class UserLoginSchema(BaseModel):
    username: str
    password_hash: str

class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_deleted: bool
    created_at: datetime



class UserOutSchema(BaseModel):
    id: int
    email: str
    username: str

    class Config:
        from_attributes = True


class UserLogoutSchema(BaseModel):
    token: str
