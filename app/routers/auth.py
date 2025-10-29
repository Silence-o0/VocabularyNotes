import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import TokenResponse
from app.utils.auth_utils import create_access_token, jwt_decode, pwd_context

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(select(User).where(User.username == form_data.username)).one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = create_access_token({"sub": str(user.id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/email_verify", status_code=status.HTTP_200_OK)
def email_verify(
    token: str,
    db: Annotated[Session, Depends(get_db)],
):
    email = jwt_decode(token)
    user = db.execute(select(User).where(User.email == email)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = UserRole.AuthorizedUser
    db.commit()


@router.get("/email_change_verify", status_code=status.HTTP_200_OK)
def email_change(
    token: str,
    db: Annotated[Session, Depends(get_db)],
):
    token_data = jwt_decode(token)
    user = db.execute(select(User).where(User.id == token_data["user_id"])).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = token_data["new_email"]
    db.commit()
