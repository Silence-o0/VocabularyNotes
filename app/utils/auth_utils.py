import os
from datetime import timedelta

from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.utils.datetime_utils import utc_now

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
PASSWORD_CRYPT = os.environ["PASSWORD_CRYPT"]

# auth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
auth_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=[PASSWORD_CRYPT], deprecated="auto")


def create_access_token(data: dict, minutes_delta: int):
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=minutes_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def jwt_decode(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" in payload:
            sub = payload.get("sub")
            return sub
    except JWTError as err:
        raise ValueError from err
    return payload
