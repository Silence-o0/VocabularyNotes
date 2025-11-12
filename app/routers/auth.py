from fastapi import APIRouter, HTTPException, status

from app import models, schemas
from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import DbSessionDep
from app.exceptions import NotFoundError
from app.services import users
from app.utils.auth_utils import create_access_token, jwt_decode

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: schemas.UserLogin,
    db: DbSessionDep,
) -> schemas.TokenResponse:
    try:
        user = users.get_user_by_username(form_data.username, db)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from None

    if not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = create_access_token({"sub": str(user.id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.TokenResponse(access_token=token, token_type="bearer")


@router.get("/email_verify", status_code=status.HTTP_200_OK)
def email_verify(token: str, db: DbSessionDep) -> None:
    try:
        email = jwt_decode(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None

    try:
        user = users.get_user_by_email(email, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

    user.role = models.UserRole.AuthorizedUser
    db.commit()
    # TODO: Redirect to frontend after email verification


@router.get("/email_change_verify", status_code=status.HTTP_200_OK)
def email_change_verify(token: str, db: DbSessionDep) -> None:
    try:
        token_data = jwt_decode(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None

    try:
        user = users.get_user_by_id(token_data["user_id"], db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None

    user.email = token_data["new_email"]
    db.commit()
    # TODO: Redirect to frontend after email changing verification
