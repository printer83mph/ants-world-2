from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from repo.abstract.users import UsersRepo
from repo.models.users import User, UserCreate

from app import schemas
from app.config import settings
from app.dependencies import get_current_user_from_token, get_users_repo
from app.helpers import auth

router = APIRouter(tags=["authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: schemas.SignupRequest,
    users: Annotated[UsersRepo, Depends(get_users_repo)],
) -> schemas.BaseResponse:
    existing_user = await users.get_by_username(request.username)
    if existing_user is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="An account with that username already exists",
        )

    # do password hashing
    hashed_password = auth.get_password_hash(request.password)

    _ = await users.create(
        UserCreate(
            username=request.username,
            hashed_password=hashed_password,
        )
    )
    return schemas.BaseResponse(message="Account successfully created!")


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: Annotated[UsersRepo, Depends(get_users_repo)],
) -> schemas.TokenResponse:
    user = await auth.authenticate_user(users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str, users: Annotated[UsersRepo, Depends(get_users_repo)]
) -> schemas.TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = auth.verify_token(refresh_token, "refresh")
    if username is None:
        raise credentials_exception

    user = await users.get_by_username(username)
    if user is None:
        raise credentials_exception

    # Generate new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

    new_access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    new_refresh_token = auth.create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return schemas.TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/profile")
def get_profile(
    current_user: Annotated[User, Depends(get_current_user_from_token)],
) -> schemas.UserGetResponse:
    return schemas.UserGetResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
    )


@router.get("/validate")
async def validate_token(
    token: str,
    users: Annotated[UsersRepo, Depends(get_users_repo)],
) -> schemas.UserGetResponse:
    """Internal endpoint for other services to validate tokens"""
    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await users.get_by_username(username)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return schemas.UserGetResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
    )
