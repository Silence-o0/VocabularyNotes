from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.models import User
from app.utils.auth_utils import auth_scheme, jwt_decode


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def current_user(
    token: Annotated[str, Depends(auth_scheme)], db: Annotated[Session, Depends(get_db)]
):
    try:
        user_id = jwt_decode(token)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired session",
        ) from err

    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
