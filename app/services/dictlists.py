from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from app.filters_schemas import DictListFilter
from app.services import languages as lang_service


def create_dictlist(dictlist: schemas.DictListCreate, user: models.User, db: Session):
    try:
        language = None
        if dictlist.lang_code:
            language = lang_service.get_language_by_code(dictlist.lang_code, db)

        db_dictlist = models.DictList(
            name=dictlist.name,
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


def get_own_dictlist_by_id(
    dictlist_id: int, user_id: UUID, db: Session
) -> models.DictList:
    dictlist = get_dictlist_by_id(dictlist_id, db)
    if dictlist.user_id != user_id:
        raise ForbiddenError
    return dictlist


def get_all_dictlists_with_filters(filters: DictListFilter, user_id: UUID, db: Session):
    query = select(models.DictList).where(models.DictList.user_id == user_id)

    if filters.lang_code:
        query = query.where(models.DictList.lang_code == filters.lang_code)

    if filters.word_id:
        query = query.where(
            models.DictList.words.any(models.Word.id == filters.word_id)
        )
    return db.scalars(query).all()


def delete_dictlist(dictlist_id: int, db: Session):
    dictlist = get_dictlist_by_id(dictlist_id, db)
    db.delete(dictlist)
    db.commit()
