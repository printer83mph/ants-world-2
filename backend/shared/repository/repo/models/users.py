import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    id: uuid.UUID
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str = Field(max_length=32)
    hashed_password: str


class UserUpdate(BaseModel):
    username: str = Field(max_length=32, default="")
    hashed_password: str = ""
