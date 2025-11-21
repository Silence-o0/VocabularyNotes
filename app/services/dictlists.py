from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError, NotFoundError
from app.services import languages as lang_services


def create_dictlist(dictlist: schemas.DictListCreate, user: models.User, db: Session):
    try:
        language = None
        if dictlist.lang_code:
            language = lang_services.get_language_by_code(dictlist.lang_code, db)

        db_dictlist = models.DictList(
            name = dictlist.name,
            max_words_limit=dictlist.max_words_limit,
            language=language,
            user=user,
        )
        db.add(db_dictlist)
        db.commit()
        db.refresh(db_dictlist)
        return db_dictlist
    except IntegrityError:
        db.rollback()
        raise AlreadyExistsError from None


def get_dictlist_by_id(dictlist_id: int, db: Session):
    dictlist = db.get(models.DictList, dictlist_id)
    if not dictlist:
        raise NotFoundError
    return dictlist


def delete_dictlist(dictlist_id: int, db: Session):
    dictlist = get_dictlist_by_id(dictlist_id, db)
    db.delete(dictlist)
    db.commit()
