import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import User
from app.services import users
from app.utils.auth_utils import auth_scheme, create_access_token, pwd_context
from app.utils.email_utils import send_verification_email

VERIFY_TOKEN_EXPIRE_MINUTES = os.getenv("VERIFY_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request, user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]
):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    verify_token = create_access_token({"sub": user.email}, VERIFY_TOKEN_EXPIRE_MINUTES)
    await send_verification_email(request, user.email, verify_token, "email_verify")
    return users.create_user(db, user)


@router.get("/me")
def get_current_user(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    return users.current_user(token, db)


@router.patch("/me/change_username", status_code=status.HTTP_200_OK)
def update_username(
    new_username: str,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(auth_scheme)],
):
    user = users.current_user(token, db)
    user.username = new_username
    db.commit()
    return {"msg": "Username successfully updated"}


@router.patch("/me/change_email", status_code=status.HTTP_200_OK)
async def update_email(
    new_email: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(auth_scheme)],
):
    user = users.current_user(token, db)
    token_data = {"new_email": new_email, "user_id": str(user.id)}
    verify_token = create_access_token(token_data, VERIFY_TOKEN_EXPIRE_MINUTES)
    await send_verification_email(
        request, new_email, verify_token, "email_change_verify"
    )
    return {"msg": "Verification link was successfully sent"}


@router.patch("/me/change_password", status_code=status.HTTP_200_OK)
def update_password(
    old_password: str,
    new_password: str,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(auth_scheme)],
):
    user = users.current_user(token, db)
    if not pwd_context.verify(old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )
    hashed_new_password = pwd_context.hash(new_password)
    user.password = hashed_new_password
    db.commit()
    return {"msg": "Password successfully updated"}


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_user(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    user = users.current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"msg": "User account has been successfully deleted"}


@router.get("/all")
def get_all_users(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    users = db.query(User).all()
    return users


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: UUID, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
