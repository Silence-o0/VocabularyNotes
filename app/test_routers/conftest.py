import os
from typing import Any, Generator

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

load_dotenv()

os.environ["DATABASE_URL"] = "sqlite:///./test_db.db"

from app.database import engine, get_db  # noqa: E402
from app.models import Base  # noqa: E402
from app.routers import auth, users  # noqa: E402


def start_application():
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(users.router)
    return app


SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def app() -> Generator[FastAPI, Any, None]:
    Base.metadata.create_all(engine)
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
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
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
