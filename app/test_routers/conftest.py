from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)


SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def app() -> Generator[FastAPI, Any, None]:
    Base.metadata.create_all(test_engine)

    from app.main import app

    yield app

    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(
    app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:
    from app.database import get_db

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
