from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError, NotFoundError


def create_language(lang: schemas.LanguageSchema, db: Session):
    try:
        db_lang = models.Language(**lang.model_dump())
        db.add(db_lang)
        db.commit()
        db.refresh(db_lang)
        return db_lang
    except IntegrityError:
        db.rollback()
        raise AlreadyExistsError from None


def get_language_by_code(code: str, db: Session):
    lang = db.get(models.Language, code)
    if not lang:
        raise NotFoundError
    return lang


def get_all_languages(db: Session):
    langs = db.scalars(select(models.Language)).all()
    return langs


def delete_language(lang, db: Session):
    db.delete(lang)
    db.commit()
