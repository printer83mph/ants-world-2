import abc
import uuid
from collections.abc import Iterator, Sequence

from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate


class SimSnapshotsRepo(abc.ABC):
    @abc.abstractmethod
    def publish(self, create: SimSnapshotCreate) -> SimSnapshot: ...

    @abc.abstractmethod
    def subscribe(self) -> Iterator[SimSnapshot]: ...

    @abc.abstractmethod
    def get_last_x(self, count: int) -> Sequence[SimSnapshot]: ...

    # utility for ants
    @abc.abstractmethod
    def get_ant_index_by_id(
        self, snapshot: SimSnapshot, id: uuid.UUID
    ) -> int | None: ...
