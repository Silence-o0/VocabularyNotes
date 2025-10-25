from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth_utils import auth_scheme, pwd_context
from app.database import get_db
from app.models import User
from app import crud, schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    return crud.create_user(db, user)


@router.get("/all")
def get_all_users(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(auth_scheme)]
):
    users = db.query(User).all()
    return users
