from fastapi import APIRouter, HTTPException, status

from app import models, schemas
from app.dependencies import CurrentUserDep, DbSessionDep, DictlistFiltersDep
from app.exceptions import ForbiddenError, NotFoundError
from app.services import dictlists as dictlist_service
from app.services import languages as lang_service

router = APIRouter(prefix="/dictlists", tags=["dictlists"])


@router.post(
    "/", response_model=schemas.DictListResponse, status_code=status.HTTP_201_CREATED
)
def create_dictlist(
    dictlist: schemas.DictListCreate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> models.DictList:
    try:
        dictlist = dictlist_service.create_dictlist(dictlist, current_user, db)
    except (ValueError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    return dictlist


@router.get(
    "/",
    response_model=list[schemas.DictListResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_dictlists(
    filters: DictlistFiltersDep, db: DbSessionDep, current_user: CurrentUserDep
) -> list[models.DictList]:
    return dictlist_service.get_all_dictlists_with_filters(filters, current_user.id, db)


@router.get(
    "/{dictlist_id}",
    response_model=schemas.DictListResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_dictlist_by_id(
    dictlist_id: int, db: DbSessionDep, current_user: CurrentUserDep
) -> models.DictList:
    try:
        dictlist = dictlist_service.get_dictlist_by_id(dictlist_id, db)
        if dictlist.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return dictlist


@router.delete("/{dictlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dictlist(
    dictlist_id: int, db: DbSessionDep, current_user: CurrentUserDep
) -> None:
    try:
        dictlist = dictlist_service.get_dictlist_by_id(dictlist_id, db)
        if dictlist.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
        return dictlist_service.delete_dictlist(dictlist_id, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.patch(
    "/{dictlist_id}",
    response_model=schemas.DictListResponse,
    status_code=status.HTTP_200_OK,
)
def update_dictlist(
    dictlist_id: int,
    body: schemas.DictListUpdate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> models.DictList:
    try:
        dictlist = dictlist_service.get_dictlist_by_id(dictlist_id, db)
        if dictlist.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = body.model_dump(exclude_unset=True)

        if "name" in update_data:
            if update_data["name"] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            dictlist.name = update_data["name"]

        if "lang_code" in update_data:
            if update_data["lang_code"] is None:
                dictlist.language = None
            else:
                language = lang_service.get_language_by_code(
                    update_data["lang_code"], db
                )
                dictlist.language = language

        db.commit()
        db.refresh(dictlist)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from None
    return dictlist


@router.post("/{dictlist_id}/assign-words", status_code=status.HTTP_204_NO_CONTENT)
def assign_word_to_dictlist(
    dictlist_id: int,
    words_body: schemas.AssignWordsRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
):
    try:
        dictlist, word_list = dictlist_service.words_to_dictlist(
            dictlist_id, words_body.word_ids, current_user.id, db
        )
        existing_word_ids = {word.id for word in dictlist.words}
        words_to_assign = [
            word for word in word_list if word.id not in existing_word_ids
        ]

        current_count = len(dictlist.words)
        new_word_count = len(words_to_assign)

        if (
            dictlist.max_words_limit is not None
            and current_count + new_word_count > dictlist.max_words_limit
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        dictlist.words.extend(words_to_assign)
        db.commit()
    except (ValueError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    except ForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        ) from None


@router.post("/{dictlist_id}/unassign-words", status_code=status.HTTP_204_NO_CONTENT)
def unassign_words_from_dictlist(
    dictlist_id: int,
    words_body: schemas.AssignWordsRequest,
    db: DbSessionDep,
    current_user: CurrentUserDep,
):
    try:
        dictlist, word_list = dictlist_service.words_to_dictlist(
            dictlist_id, words_body.word_ids, current_user.id, db
        )
        existing_word_ids = {word.id for word in dictlist.words}
        words_to_remove = [word for word in word_list if word.id in existing_word_ids]

        for word in words_to_remove:
            dictlist.words.remove(word)
        db.commit()
    except (ValueError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    except ForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        ) from None
