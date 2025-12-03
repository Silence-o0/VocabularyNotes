from fastapi import APIRouter, HTTPException, status

from app import models, schemas
from app.dependencies import CurrentUserDep, DbSessionDep
from app.exceptions import NotFoundError
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
def get_all_dictlists(current_user: CurrentUserDep) -> list[schemas.DictListResponse]:
    return current_user.dict_lists


@router.get(
    "/{dictlist_id}",
    response_model=schemas.DictListResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_dictlist_by_id(
    dictlist_id: int, db: DbSessionDep, current_user: CurrentUserDep
) -> schemas.DictListResponse:
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
) -> schemas.DictListResponse:
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
