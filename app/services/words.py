from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError, NotFoundError
from app.services import languages as lang_services


def create_word(word: schemas.WordCreate, user: models.User, db: Session):
    try:
        language = lang_services.get_language_by_code(word.lang_code, db)

        db_word = models.Word(
            new_word=word.new_word,
            translation=word.translation,
            note=word.note,
            language=language,
            user=user,
        )

        if word.contexts:
            db_word.contexts_list = word.contexts

        db.add(db_word)
        db.commit()
        db.refresh(db_word)
        return db_word

    except IntegrityError:
        db.rollback()
        raise AlreadyExistsError from None


def get_word_by_id(word_id: int, db: Session):
    word = db.get(models.Word, word_id)
    if not word:
        raise NotFoundError
    return word


def delete_word(word_id: int, db: Session):
    word = get_word_by_id(word_id, db)
    db.delete(word)
    db.commit()
