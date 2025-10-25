import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.auth_utils import auth_scheme, create_access_token, pwd_context
from app.database import get_db
from app.email_utils import send_verification_email
from app.models import User
from app.services.users import current_user

VERIFY_TOKEN_EXPIRE_MINUTES = os.getenv("VERIFY_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    verify_token = create_access_token({"sub": user.email}, VERIFY_TOKEN_EXPIRE_MINUTES)
    await send_verification_email(request, user.email, verify_token)
    return crud.create_user(db, user)


@router.get("/me")
def get_current_user(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    return current_user(token, db)


@router.get("/all")
def get_all_users(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    users = db.query(User).all()
    return users
