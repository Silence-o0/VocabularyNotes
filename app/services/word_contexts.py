from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.exceptions import AlreadyExistsError
from app.services import languages as lang_services


# def create_word_context(word: schemas.WordCreate, user: models.User, db: Session):
#     try:
#         language = lang_services.get_language_by_code(word.lang_code, db)


#     except IntegrityError:
#         db.rollback()
#         raise AlreadyExistsError from None
