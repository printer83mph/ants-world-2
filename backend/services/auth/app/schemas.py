import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    username: str = Field(max_length=32)
    password: str = Field(max_length=128)


class BaseResponse(BaseModel):
    message: Optional[str] = None


class TokenResponse(BaseResponse):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserGetResponse(BaseModel):
    id: uuid.UUID
    username: str
    created_at: datetime
