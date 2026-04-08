import uuid
from typing import Optional

import pydantic as pd


class User(pd.BaseModel):
    model_config = pd.ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    hashed_password: str


class UserCreate(pd.BaseModel):
    username: str = pd.Field(max_length=32)
    hashed_password: str


class UserUpdate(pd.BaseModel):
    username: Optional[str] = pd.Field(max_length=32, default=None)
    hashed_password: Optional[str] = None
