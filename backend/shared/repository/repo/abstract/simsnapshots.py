import abc
import uuid
from collections.abc import Sequence

from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate


class SimSnapshotsRepo(abc.ABC):
    @abc.abstractmethod
    def create(self, create: SimSnapshotCreate) -> SimSnapshot: ...

    @abc.abstractmethod
    def get_latest_x(self, count: int) -> Sequence[SimSnapshot]: ...

    @abc.abstractmethod
    def get_by_id(self, id: uuid.UUID) -> SimSnapshot | None: ...

    @abc.abstractmethod
    def get_ant_index_by_id(
        self, snapshot: SimSnapshot, id: uuid.UUID
    ) -> int | None: ...
