from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as orm


# Base class for all models
class Base(orm.DeclarativeBase, orm.MappedAsDataclass):
    pass


class TimestampedBase(Base):
    __abstract__ = True

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )
    updated_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.TIMESTAMP(timezone=True),
        default_factory=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
