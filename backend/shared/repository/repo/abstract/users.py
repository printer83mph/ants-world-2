import abc
import uuid

from repo.models.users import User, UserCreate, UserUpdate


class UsersRepo(abc.ABC):
    @abc.abstractmethod
    async def create(self, create: UserCreate) -> User: ...

    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> User | None: ...

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User | None: ...

    @abc.abstractmethod
    async def update(self, id: uuid.UUID, update: UserUpdate) -> User: ...
