from typing import Annotated, Generator

import db.engine_async as engine
from fastapi import Depends, HTTPException, Request, status
from repo.abstract import users as users_abstract
from repo.impl import users as users_impl
from repo.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.helpers import auth

_async_engine = engine.create_async_engine(config.settings.database_url)
_async_sessionmaker = engine.create_async_session(_async_engine)

get_db = engine.get_database_dependency(_async_sessionmaker)


def get_users_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Generator[users_abstract.UsersRepo, None, None]:
    yield users_impl.UsersRepo(db)


async def get_current_user(
    request: Request,
    users: Annotated[users_abstract.UsersRepo, Depends(get_users_repo)],
) -> User:
    """Legacy function for cookie-based authentication - used for backward compatibility"""

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await users.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def get_current_user_from_token(
    token: Annotated[str, Depends(auth.oauth2_scheme)],
    users: Annotated[users_abstract.UsersRepo, Depends(get_users_repo)],
) -> User:
    """OAuth2 compliant function for bearer token authentication"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = auth.verify_token(token, "access")
    if username is None:
        raise credentials_exception

    user = await users.get_by_username(username)
    if user is None:
        raise credentials_exception

    return user
