from pydantic import BaseModel, EmailStr, SecretStr, constr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: constr(min_length=4, max_length=50, pattern=r"^\w+$")
    email: EmailStr
    password: constr(min_length=6)


class PasswordChangeRequest(BaseModel):
    current_password: SecretStr
    new_password: SecretStr
