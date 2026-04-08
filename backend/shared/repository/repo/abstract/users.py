import abc
import uuid
from typing import Optional

from models.users import User, UserCreate, UserUpdate


class UsersRepo(abc.ABC):
    @abc.abstractmethod
    async def create(self, create: UserCreate) -> User: ...

    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[User]: ...

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: ...

    @abc.abstractmethod
    async def update(self, id: uuid.UUID, update: UserUpdate) -> User: ...
