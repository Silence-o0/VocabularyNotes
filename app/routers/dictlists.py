from fastapi import APIRouter, HTTPException, status

from app import schemas
from app.dependencies import CurrentUserDep, DbSessionDep
from app.exceptions import NotFoundError
from app.services import dictlists as dictlist_service

router = APIRouter(prefix="/dictlists", tags=["dictlists"])


@router.post(
    "/", response_model=schemas.DictListResponse, status_code=status.HTTP_201_CREATED
)
def create_dictlist(
    dictlist: schemas.DictListCreate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> schemas.DictListResponse:
    try:
        dictlist = dictlist_service.create_dictlist(dictlist, current_user, db)
    except (ValueError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    return dictlist
