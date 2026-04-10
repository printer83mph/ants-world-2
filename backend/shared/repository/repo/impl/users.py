import uuid
from typing import Optional

from db.models import UsersTable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repo.abstract import users as abstract
from repo.models.users import User, UserCreate, UserUpdate


def _to_model(db_user: UsersTable) -> User:
    return User.model_validate(db_user, from_attributes=True)


class UsersRepo(abstract.UsersRepo):
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, create: UserCreate) -> User:
        new_user = UsersTable(**create.model_dump(mode="python"))
        self.db.add(new_user)
        await self.db.flush()

        new_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.id == new_user.id)
        )
        new_user_orm = _to_model(new_user_rows.scalar_one())

        await self.db.commit()
        return new_user_orm

    async def get_by_id(self, id: uuid.UUID) -> Optional[User]:
        existing_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.id == id)
        )
        existing_user = existing_user_rows.scalar()

        if existing_user is None:
            return None
        return _to_model(existing_user)

    async def get_by_username(self, username: str) -> Optional[User]:
        existing_user_rows = await self.db.execute(
            select(UsersTable).where(UsersTable.username == username)
        )
        existing_user = existing_user_rows.scalar()

        if existing_user is None:
            return None
        return _to_model(existing_user)

    async def update(self, id: uuid.UUID, update: UserUpdate) -> User:
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

        return _to_model(updated_user)
