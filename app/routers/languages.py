
from fastapi import APIRouter, HTTPException, status

from app import schemas
from app.dependencies import AdminRoleDep, DbSessionDep
from app.exceptions import AlreadyExistsError, NotFoundError
from app.services import languages as lang_service

router = APIRouter(prefix="/languages", tags=["languages"])


@router.post(
    "/", response_model=schemas.LanguageSchema, status_code=status.HTTP_201_CREATED
)
def create_language(
    lang: schemas.LanguageSchema,
    db: DbSessionDep,
    current_user: AdminRoleDep,
) -> schemas.LanguageSchema:
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


@router.delete("/{lang_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_language(
    lang_code: str, db: DbSessionDep, current_user: AdminRoleDep
) -> None:
    try:
        return lang_service.delete_language(lang_code, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None


@router.get(
    "/all", response_model=list[schemas.LanguageSchema], status_code=status.HTTP_200_OK
)
def get_all_languages(db: DbSessionDep) -> list[schemas.LanguageSchema]:
    return lang_service.get_all_languages(db)


@router.get(
    "/{lang_code}",
    response_model=schemas.LanguageSchema,
    status_code=status.HTTP_200_OK,
)
def get_language_by_code(lang_code: str, db: DbSessionDep) -> schemas.LanguageSchema:
    try:
        lang = lang_service.get_language_by_code(lang_code, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return lang


@router.patch("/{lang_code}", status_code=status.HTTP_200_OK)
def update_lang_name(
    body: schemas.LanguageUpdate,
    lang_code: str,
    current_user: AdminRoleDep,
    db: DbSessionDep,
) -> None:
    try:
        lang = lang_service.get_language_by_code(lang_code, db)
        if lang.name == body.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        lang.name = body.name
        db.commit()
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from None
