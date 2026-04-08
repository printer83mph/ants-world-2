import abc
import uuid
from typing import Optional

from models.users import User, UserCreate, UserUpdate


class UsersRepo(abc.ABC):
    @abc.abstractmethod
    def create(self, create: UserCreate) -> User: ...

    @abc.abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[User]: ...

    @abc.abstractmethod
    def get_by_username(self, create: UserCreate) -> User: ...

    @abc.abstractmethod
    def update(self, id: uuid.UUID, update: UserUpdate) -> User: ...
