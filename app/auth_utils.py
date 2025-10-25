import os
from datetime import timedelta

from fastapi.security import HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from app.utils import utc_now

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = os.getenv("ACCESS_TOKEN_EXPIRE_HOURS")

# auth_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = utc_now() + timedelta(hours=int(ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
