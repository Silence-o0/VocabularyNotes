from pydantic import BaseModel, EmailStr, constr


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: constr(min_length=4, max_length=50, pattern=r"^\w+$")
    email: EmailStr
    password: constr(min_length=6)
