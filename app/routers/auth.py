import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.utils.auth_utils import create_access_token, jwt_decode, pwd_context

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": str(user.id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/email_verify", status_code=status.HTTP_200_OK)
async def email_verify(
    token: str,
    db: Annotated[Session, Depends(get_db)],
):
    email = jwt_decode(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = UserRole.AuthorizedUser
    db.commit()
    return {"msg": "Email successfully verified!"}


@router.get("/email_change_verify", status_code=status.HTTP_200_OK)
async def email_change(
    token: str,
    db: Annotated[Session, Depends(get_db)],
):
    token_data = jwt_decode(token)
    user = db.query(User).get(token_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = token_data["new_email"]
    db.commit()
    return {"msg": "Email successfully updated!"}
