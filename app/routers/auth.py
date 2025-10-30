import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import DbSessionDep
from app.models import UserRole
from app.schemas import TokenResponse
from app.services import users
from app.utils.auth_utils import create_access_token, jwt_decode, pwd_context

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSessionDep,
):
    try:
        user = users.get_user_by_username(form_data.username, db)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from None

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = create_access_token({"sub": str(user.id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/email_verify", status_code=status.HTTP_200_OK)
def email_verify(token: str, db: DbSessionDep):
    try:
        email = jwt_decode(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None

    try:
        user = users.get_user_by_email(email, db)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

    user.role = UserRole.AuthorizedUser
    db.commit()


@router.get("/email_change_verify", status_code=status.HTTP_200_OK)
def email_change_verify(token: str, db: DbSessionDep):
    try:
        token_data = jwt_decode(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None

    try:
        user = users.get_user_by_id(token_data["user_id"], db)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

    user.email = token_data["new_email"]
    db.commit()
