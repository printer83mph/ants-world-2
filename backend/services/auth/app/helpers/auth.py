from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from repo.abstract.users import UsersRepo
from repo.models.users import User

from app.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "iat": now, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username = payload.get("sub")
        token_type_claim = payload.get("type")

        if not (isinstance(username, str) and isinstance(token_type_claim, str)):
            return None

        if username is None or token_type_claim != token_type:
            return None

        return username
    except JWTError:
        return None


async def authenticate_user(
    users: UsersRepo, username: str, password: str
) -> Optional[User]:
    user = await users.get_by_username(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
