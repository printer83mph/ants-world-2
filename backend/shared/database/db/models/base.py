from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


# Base class for all models
class Base(AsyncAttrs, DeclarativeBase, MappedAsDataclass):
    pass


class TimestampedBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
