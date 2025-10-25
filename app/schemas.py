from pydantic import BaseModel, EmailStr

from app.models import UserRole


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
