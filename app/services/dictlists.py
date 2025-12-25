from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError, NotFoundError, ForbiddenError
from app.services import languages as lang_service
from app.services import dictlists as dictlist_service
from app.services import words as word_service


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


def delete_dictlist(dictlist_id: int, db: Session):
    dictlist = get_dictlist_by_id(dictlist_id, db)
    db.delete(dictlist)
    db.commit()


def words_to_dictlist(
    dictlist_id: int, word_ids_list: list[int], user_id: UUID, db: Session
) -> tuple[models.DictList, list[models.Word]]:
    dictlist = dictlist_service.get_dictlist_by_id(dictlist_id, db)
    if dictlist.user_id != user_id:
        raise ForbiddenError

    if not word_ids_list:
        raise ValueError

    words = [word_service.get_word_by_id(word_id, db) for word_id in word_ids_list]
    for word in words:
        if word.user_id != user_id:
            raise ForbiddenError
    return dictlist, words
