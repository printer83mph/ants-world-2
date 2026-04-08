import uuid
from typing import Optional

from abstract import users as abstract
from db.models import UsersTable
from models import users as m
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


def _to_orm(db_user: UsersTable) -> m.User:
    return m.User.model_validate(db_user, from_attributes=True)


class UsersRepo(abstract.UsersRepo):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, create: m.UserCreate) -> m.User:
        new_user_rows = await self.db.execute(
            insert(UsersTable)
            .values(**create.model_dump(mode="python"))
            .returning(UsersTable)
        )
        return _to_orm(new_user_rows.scalars().one())

    async def get_by_id(self, id: uuid.UUID) -> Optional[m.User]:
        existing_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.id == id)
        )
        existing_user = existing_user_rows.scalar()

        if existing_user is None:
            return None
        return _to_orm(existing_user)

    async def get_by_username(self, username: str) -> Optional[m.User]:
        existing_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.username == username)
        )
        existing_user = existing_user_rows.scalar()

        if existing_user is None:
            return None
        return _to_orm(existing_user)

    async def update(self, id: uuid.UUID, update: m.UserUpdate) -> m.User:
        existing_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.id == id)
        )
        existing_user = existing_user_rows.scalars().one()

        # update only set fields
        update_fields = update.model_dump(mode="python", exclude_unset=True)
        if "username" in update_fields:
            existing_user.username = update_fields["username"]
        if "hashed_password" in update_fields:
            existing_user.hashed_password = update_fields["hashed_password"]

        await self.db.commit()

        updated_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.id == id)
        )
        updated_user = updated_user_rows.scalars().one()

        return _to_orm(updated_user)
