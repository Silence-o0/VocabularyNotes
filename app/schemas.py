from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt, SecretStr, field_validator

from app import models
from app.models import UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


Username = Annotated[str, Field(min_length=4, max_length=50, pattern=r"^\w+$")]


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: Annotated[str, Field(min_length=6)]


class UserUpdateUsername(BaseModel):
    username: Username


class UserUpdateEmail(BaseModel):
    email: EmailStr


class UserPasswordChange(BaseModel):
    old_password: SecretStr
    new_password: SecretStr


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: Username
    email: EmailStr
    role: UserRole
    created_at: datetime


LanguageCode = Annotated[
    str, Field(min_length=2, max_length=5, pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
]

LanguageName = Annotated[str, Field(min_length=1)]


class LanguageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: LanguageCode
    name: LanguageName


class LanguageUpdate(BaseModel):
    name: LanguageName


DictListName = Annotated[str, Field(min_length=1, max_length=120)]


class DictListCreate(BaseModel):
    lang_code: LanguageCode | None = None
    name: DictListName
    max_words_limit: PositiveInt | None = None


class DictListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    language: LanguageSchema | None = None
    name: DictListName
    created_at: datetime
    max_words_limit: PositiveInt | None = None


class DictListUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lang_code: LanguageCode | None = None
    name: DictListName | None = None


WordNameAndTranslation = Annotated[str, Field(min_length=1, max_length=200)]
WordNote = Annotated[str, Field(min_length=1, max_length=800)]


class WordCreate(BaseModel):
    new_word: WordNameAndTranslation
    translation: WordNameAndTranslation | None = None
    note: WordNote | None = None
    lang_code: LanguageCode
    contexts: List[str] | None = None


class WordResponse(BaseModel):
    id: int
    user_id: UUID
    new_word: WordNameAndTranslation
    translation: WordNameAndTranslation | None = None
    note: WordNote | None = None
    language: LanguageSchema
    created_at: datetime
    contexts: list[str] = []

    @field_validator('contexts', mode='before')
    @classmethod
    def extract_context_strings(cls, v):
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], models.WordContext):
            return [ctx.context for ctx in v]
        return v


