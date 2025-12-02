from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from app import models, schemas
from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import Base
from app.services import dictlists as dictlist_service
from app.services import languages as lang_service
from app.services import users as user_service
from app.services import words as word_service
from app.utils.auth_utils import create_access_token

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    from app.main import app

    return app


@pytest.fixture
def db_session() -> Generator[Session]:
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(test_engine)

    with Session(bind=test_engine) as db:
        yield db

    Base.metadata.drop_all(test_engine)


@pytest.fixture
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    from app.database import get_db

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(db_session):
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword123",
    )
    user = user_service.create_user(user_data, db_session)
    return user


@pytest.fixture
def another_user(db_session):
    user_data = schemas.UserCreate(
        username="otheruser",
        email="other@example.com",
        password="password123",
    )
    user = user_service.create_user(user_data, db_session)
    return user


@pytest.fixture
def admin(user, db_session):
    user.role = models.UserRole.Admin
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def mock_send_verification_email(mocker):
    return mocker.patch("app.routers.users.send_verification_email")


@pytest.fixture
def authorized_client(client, user):
    token = create_access_token({"sub": str(user.id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }
    return client


@pytest.fixture
def authorized_client_as_admin(authorized_client, admin):
    return authorized_client


@pytest.fixture
def language(db_session):
    lang_data = schemas.LanguageSchema(code="en-UK", name="English")
    lang = lang_service.create_language(lang_data, db_session)
    return lang


@pytest.fixture
def dictlist(user, language, db_session):
    dictlist = dictlist_service.create_dictlist(
        schemas.DictListCreate(name="My Vocabulary", lang_code="en-UK"),
        user,
        db_session,
    )
    return dictlist


@pytest.fixture
def another_user_dictlist(another_user, language, db_session):
    dictlist = dictlist_service.create_dictlist(
        schemas.DictListCreate(name="My Vocabulary", lang_code="en-UK"),
        another_user,
        db_session,
    )
    return dictlist


@pytest.fixture
def word(user, language, db_session):
    word = word_service.create_word(
        schemas.WordCreate(
            new_word="animal",
            lang_code="en-UK",
            contexts=[
                "Wild animals live in the forest",
                "My favorite animal is a dog",
            ],
        ),
        user,
        db_session,
    )
    return word


@pytest.fixture
def another_user_word(another_user, language, db_session):
    word = word_service.create_word(
        schemas.WordCreate(new_word="animal", lang_code="en-UK"),
        another_user,
        db_session,
    )
    return word
