from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app.models import UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=50, pattern=r"^\w+$")]
    email: EmailStr
    password: Annotated[str, Field(min_length=6)]


class UserUpdateUsername(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=50, pattern=r"^\w+$")]


class UserUpdateEmail(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class PasswordChangeRequest(BaseModel):
    current_password: SecretStr
    new_password: SecretStr
