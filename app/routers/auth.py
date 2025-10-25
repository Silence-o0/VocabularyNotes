from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_utils import create_access_token, pwd_context
from app.database import get_db
from app.models import User
from app import schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(request: schemas.UserLogin, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not pwd_context.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
