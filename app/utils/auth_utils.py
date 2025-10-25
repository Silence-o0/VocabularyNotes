import os
from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.utils.datetime_utils import utc_now

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

auth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# auth_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def create_access_token(data: dict, minutes_delta: int):
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=int(minutes_delta))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def jwt_decode(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" in payload:
            sub = payload.get("sub")
            return sub
    except JWTError:
        raise credentials_exception from None
    return payload
