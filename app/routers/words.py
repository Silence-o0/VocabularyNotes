from fastapi import APIRouter, HTTPException, status

from app import schemas
from app.dependencies import CurrentUserDep, DbSessionDep
from app.exceptions import NotFoundError
from app.services import languages as lang_service
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


@router.get(
    "/{word_id}",
    response_model=schemas.WordResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_word_by_id(
    word_id: int, db: DbSessionDep, current_user: CurrentUserDep
) -> schemas.WordResponse:
    try:
        word = word_service.get_word_by_id(word_id, db)
        if word.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return word


@router.get(
    "/",
    response_model=list[schemas.WordResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_words(current_user: CurrentUserDep) -> list[schemas.WordResponse]:
    return current_user.words


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(word_id: int, db: DbSessionDep, current_user: CurrentUserDep) -> None:
    try:
        word = word_service.get_word_by_id(word_id, db)
        if word.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
        return word_service.delete_word(word_id, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.patch(
    "/{word_id}",
    response_model=schemas.WordResponse,
    status_code=status.HTTP_200_OK,
)
def update_word(
    word_id: int,
    body: schemas.WordUpdate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> schemas.WordResponse:
    try:
        word = word_service.get_word_by_id(word_id, db)
        if word.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = body.model_dump(exclude_unset=True)

        if "new_word" in update_data:
            if update_data["new_word"] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            word.new_word = update_data["new_word"]

        if "translation" in update_data:
            word.translation = update_data["translation"]

        if "note" in update_data:
            word.note = update_data["note"]

        if "lang_code" in update_data:
            if update_data["lang_code"] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            else:
                language = lang_service.get_language_by_code(
                    update_data["lang_code"], db
                )
                word.language = language

        if "contexts" in update_data:
            if update_data["contexts"] is not None:
                word.contexts_list = [
                    ctx.strip() for ctx in update_data["contexts"] if ctx.strip()
                ]

        db.commit()
        db.refresh(word)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from None
    return word
