from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth_utils import ALGORITHM, SECRET_KEY, auth_scheme, jwt_decode
from app.database import get_db
from app.models import User


def current_user(
    token: Annotated[str, Depends(auth_scheme)], db: Annotated[Session, Depends(get_db)]
):
    username = jwt_decode(token)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise "Could not validate credentials"
    return user
