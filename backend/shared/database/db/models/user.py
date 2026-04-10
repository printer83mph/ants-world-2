import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import TimestampedBase


class UsersTable(TimestampedBase):
    __tablename__: str = "users"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.UUID, default_factory=uuid.uuid4, primary_key=True
    )
    username: orm.Mapped[str] = orm.mapped_column(
        sa.String(length=32), unique=True, kw_only=True
    )
    hashed_password: orm.Mapped[str] = orm.mapped_column(sa.String(), kw_only=True)
