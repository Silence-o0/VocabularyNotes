import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi_filter import FilterDepends
from sqlalchemy.orm import Session

from app import filters_schemas, models
from app.database import get_db
from app.exceptions import NotFoundError
from app.utils.auth_utils import auth_scheme, jwt_decode

DbSessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPBearer, Depends(auth_scheme)]


def current_user(token: TokenDep, db: DbSessionDep):
    from app.services import users

    try:
        user_id = uuid.UUID(jwt_decode(token.credentials))
        user = users.get_user_by_id(user_id, db)
    except (ValueError, NotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None
    return user


CurrentUserDep = Annotated[models.User, Depends(current_user)]


def check_role(current_user: CurrentUserDep, min_role: models.UserRole):
    if current_user.role < min_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return current_user


def admin_required(current_user: CurrentUserDep):
    return check_role(current_user, models.UserRole.Admin)


def full_access_required(current_user: CurrentUserDep):
    return check_role(current_user, models.UserRole.FullAccessUser)


def authorized_required(current_user: CurrentUserDep):
    return check_role(current_user, models.UserRole.AuthorizedUser)


AdminRoleDep = Annotated[models.User, Depends(admin_required)]
FullAccessDep = Annotated[models.User, Depends(full_access_required)]
AuthorizedDep = Annotated[models.User, Depends(authorized_required)]


UserFiltersDep = Annotated[
    filters_schemas.UserFilter, FilterDepends(filters_schemas.UserFilter)
]
DictlistFiltersDep = Annotated[
    filters_schemas.DictListFilter, FilterDepends(filters_schemas.DictListFilter)
]
WordFiltersDep = Annotated[
    filters_schemas.WordFilter, FilterDepends(filters_schemas.WordFilter)
]
