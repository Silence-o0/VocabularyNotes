from datetime import timedelta

from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.constants import JWT_ALGORITM, SECRET_KEY
from app.utils.datetime_utils import utc_now

auth_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def create_access_token(data: dict, minutes_delta: int):
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=minutes_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITM)


def jwt_decode(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITM])
        if "sub" in payload:
            sub = payload.get("sub")
            return sub
    except JWTError as err:
        raise ValueError from err
    return payload
