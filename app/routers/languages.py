from fastapi import APIRouter, HTTPException, status

from app import schemas
from app.dependencies import AdminRoleDep, DbSessionDep
from app.exceptions import AlreadyExistsError
from app.services import languages as lang_service

router = APIRouter(prefix="/languages", tags=["languages"])


@router.post(
    "/", response_model=schemas.LanguageSchema, status_code=status.HTTP_201_CREATED
)
def create_language(
    lang: schemas.LanguageSchema,
    db: DbSessionDep,
    current_user: AdminRoleDep,
) -> schemas.UserResponse:
    try:
        lang = lang_service.create_language(lang, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    except AlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        ) from None
    return lang
