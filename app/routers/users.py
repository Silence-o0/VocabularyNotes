import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import PasswordChangeRequest, UserCreate
from app.database import get_db
from app.models import User
from app.services import users
from app.utils.auth_utils import auth_scheme, create_access_token, pwd_context
from app.utils.email_utils import send_verification_email

VERIFY_TOKEN_EXPIRE_MINUTES = int(os.environ["VERIFY_TOKEN_EXPIRE_MINUTES"])

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    request: Request, user: UserCreate, background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)]
):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    verify_token = create_access_token({"sub": user.email}, VERIFY_TOKEN_EXPIRE_MINUTES)
    background_tasks.add_tasks(send_verification_email, request=request, 
                            email=user.email, token=verify_token, action="email_verify")
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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


@router.patch("/me/change_email", status_code=status.HTTP_202_ACCEPTED)
def update_email(
    new_email: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(auth_scheme)],
):
    user = users.current_user(token, db)
    token_data = {"new_email": new_email, "user_id": str(user.id)}
    verify_token = create_access_token(token_data, VERIFY_TOKEN_EXPIRE_MINUTES)
    background_tasks.add_tasks(send_verification_email, request=request, 
                            email=user.email, token=verify_token, action="email_change_verify")


@router.patch("/me/change_password", status_code=status.HTTP_200_OK)
def update_password(
    body: PasswordChangeRequest,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(auth_scheme)],
):
    user = users.current_user(token, db)
    if not pwd_context.verify(body.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )
    hashed_new_password = pwd_context.hash(body.new_password)
    user.password = hashed_new_password
    db.commit()


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


@router.get("/all")
def get_all_users(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    users = db.execute(select(User)).all()
    return users


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: UUID, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
