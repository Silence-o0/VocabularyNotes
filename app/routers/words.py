from fastapi import APIRouter, HTTPException, status

from app import schemas
from app.dependencies import CurrentUserDep, DbSessionDep
from app.exceptions import NotFoundError
from app.services import words as word_service

router = APIRouter(prefix="/words", tags=["words"])


@router.post(
    "/", response_model=schemas.WordResponse, status_code=status.HTTP_201_CREATED
)
def create_word(
    word: schemas.WordCreate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> schemas.WordResponse:
    try:
        word = word_service.create_word(word, current_user, db)
    except (ValueError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    return word
