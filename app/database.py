from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.constants import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    with SessionLocal() as db:
        yield db
