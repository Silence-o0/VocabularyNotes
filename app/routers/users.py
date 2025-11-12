from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from psycopg import IntegrityError

from app import schemas
from app.constants import VERIFY_TOKEN_EXPIRE_MINUTES
from app.dependencies import CurrentUserDep, DbSessionDep
from app.exceptions import NotFoundError
from app.services import users as user_service
from app.utils.auth_utils import create_access_token, pwd_context
from app.utils.email_utils import send_verification_email

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: DbSessionDep,
) -> schemas.UserResponse:
    try:
        user = user_service.create_user(user, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from None
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        ) from None

    verify_token = create_access_token({"sub": user.email}, VERIFY_TOKEN_EXPIRE_MINUTES)
    background_tasks.add_task(
        send_verification_email,
        request=request,
        email=user.email,
        token=verify_token,
        action="email_verify",
    )
    return user


@router.get("/me", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def get_current_user(current_user: CurrentUserDep) -> schemas.UserResponse:
    return current_user


@router.patch("/me/change_username", status_code=status.HTTP_200_OK)
def update_username(
    body: schemas.UserUpdateUsername, current_user: CurrentUserDep, db: DbSessionDep
) -> None:
    try:
        current_user.username = body.username
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from None


@router.patch("/me/change_email", status_code=status.HTTP_202_ACCEPTED)
def update_email(
    body: schemas.UserUpdateEmail,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> None:
    if current_user.email == body.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        # We need to check that no user already has this email.
        # If get_user_by_email didn't raise a NotFoundError, such a user
        # does exist, and the check failed.
        user_service.get_user_by_email(body.email, db)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    except NotFoundError:
        pass

    token_data = {"new_email": body.email, "user_id": str(current_user.id)}
    verify_token = create_access_token(token_data, VERIFY_TOKEN_EXPIRE_MINUTES)
    background_tasks.add_task(
        send_verification_email,
        request=request,
        email=current_user.email,
        token=verify_token,
        action="email_change_verify",
    )


@router.patch("/me/change_password", status_code=status.HTTP_200_OK)
def update_password(
    body: schemas.UserPasswordChange,
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> None:
    if not current_user.verify_password(body.old_password.get_secret_value()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    current_user.password = pwd_context.hash(body.new_password.get_secret_value())
    db.commit()


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_user(current_user: CurrentUserDep, db: DbSessionDep) -> None:
    return user_service.delete_user(current_user, db)


@router.get(
    "/all", response_model=list[schemas.UserResponse], status_code=status.HTTP_200_OK
)
def get_all_users(
    db: DbSessionDep, current_user: CurrentUserDep
) -> list[schemas.UserResponse]:
    return user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_by_id(
    user_id: UUID, db: DbSessionDep, current_user: CurrentUserDep
) -> schemas.UserResponse:
    try:
        user = user_service.get_user_by_id(user_id, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from None
    return user
