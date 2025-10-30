from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import users
from app.utils.auth_utils import auth_scheme, jwt_decode

DbSessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(auth_scheme)]


def current_user(token: TokenDep, db: DbSessionDep):
    try:
        user_id = jwt_decode(token)
        user = users.get_user_by_id(user_id, db)
    except (ValueError, LookupError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from None
    return user


CurrentUserDep = Annotated[models.User, Depends(current_user)]
