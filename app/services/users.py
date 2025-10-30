from uuid import UUID

from sqlalchemy import select

from app import models, schemas
from app.dependencies import DbSessionDep
from app.utils.auth_utils import pwd_context


def create_user(user: schemas.UserCreate, db: DbSessionDep):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(user_id: UUID, db: DbSessionDep):
    user = db.get(models.User, user_id)
    if not user:
        raise LookupError
    return user


def get_user_by_username(username: str, db: DbSessionDep):
    user = db.scalars(
        select(models.User).where(models.User.username == username)
    ).one_or_none()
    if not user:
        raise LookupError
    return user


def get_user_by_email(email: str, db: DbSessionDep):
    user = db.scalars(
        select(models.User).where(models.User.email == email)
    ).one_or_none()
    if not user:
        raise LookupError
    return user


def get_all_users(db: DbSessionDep):
    users = db.scalars(select(models.User)).all()
    return users


def delete_user(user, db: DbSessionDep):
    db.delete(user)
    db.commit()
