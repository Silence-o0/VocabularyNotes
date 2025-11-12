import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.utils.auth_utils import auth_scheme, jwt_decode

DbSessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPBearer, Depends(auth_scheme)]

from app import models  # noqa: E402
from app.services import users  # noqa: E402


def current_user(token: TokenDep, db: DbSessionDep):
    try:
        user_id = uuid.UUID(jwt_decode(token.credentials))
        user = users.get_user_by_id(user_id, db)
    except (ValueError, NotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None
    return user


CurrentUserDep = Annotated[models.User, Depends(current_user)]
