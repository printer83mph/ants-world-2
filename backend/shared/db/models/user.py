import uuid

import pydantic as pd
import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import TimestampedBase

# --- SQLAlchemy table


class UserTable(TimestampedBase):
    __tablename__ = "users"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.UUID, default_factory=uuid.uuid4, primary_key=True
    )
    username: orm.Mapped[str] = orm.mapped_column(
        sa.String(length=32), unique=True, kw_only=True
    )
    hashed_password: orm.Mapped[str] = orm.mapped_column(sa.String(), kw_only=True)


# --- Pydantic models


class User(pd.BaseModel):
    model_config = pd.ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    hashed_password: str


class UserCreate(pd.BaseModel):
    username: str = pd.Field(max_length=32)
    hashed_password: str
