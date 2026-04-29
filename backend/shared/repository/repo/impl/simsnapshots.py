import uuid
from collections.abc import Sequence
from typing import override

import redis

from repo.abstract import simsnapshots as abstract
from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate

# TODO: write protobuf serialization/deserialization stuff


class SimSnapshotsRepo(abstract.SimSnapshotsRepo):
    def __init__(self, redis_engine: redis.Redis):
        self.redis: redis.Redis = redis_engine

    @override
    def create(self, create: SimSnapshotCreate) -> SimSnapshot:
        raise NotImplementedError()

    @override
    def get_latest_x(self, count: int) -> Sequence[SimSnapshot]:
        raise NotImplementedError()

    @override
    def get_by_id(self, id: uuid.UUID) -> SimSnapshot | None:
        raise NotImplementedError()

    @override
    def get_ant_index_by_id(self, snapshot: SimSnapshot, id: uuid.UUID) -> int | None:
        raise NotImplementedError()
