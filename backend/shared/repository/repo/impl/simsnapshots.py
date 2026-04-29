import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import override

import numpy as np
import redis

from protopy.ant_simulation import simsnapshot_pb2
from repo.abstract import simsnapshots as abstract
from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate


def _to_model(serialized_snapshot: bytes) -> SimSnapshot:
    """
    Deserializes a snapshot from bytes into a Pydantic model
    """

    sim_snapshot = simsnapshot_pb2.SimSnapshot()
    _ = sim_snapshot.ParseFromString(serialized_snapshot)

    return SimSnapshot(
        id=uuid.UUID(sim_snapshot.id),
        ant_ids=np.array(sim_snapshot.ant_ids, "S16"),
        ant_positions=np.array(
            ([ant.x, ant.y] for ant in sim_snapshot.ants), np.float64
        ),
        ant_rotations=np.array((ant.rotation for ant in sim_snapshot.ants), np.float64),
        ant_pheremone_sensitivities=np.array(
            (ant.pheremone_sensitivity for ant in sim_snapshot.ants), np.float64
        ),
        ant_pheremone_strengths=np.array(
            (ant.pheremone_strength for ant in sim_snapshot.ants), np.float64
        ),
        ant_speeds=np.array((ant.speed for ant in sim_snapshot.ants), np.float64),
        ant_seconds_of_life_left=np.array(
            (ant.seconds_of_life_left for ant in sim_snapshot.ants), np.float64
        ),
        crumb_positions=np.array(
            ([crumb.x, crumb.y] for crumb in sim_snapshot.crumbs), np.float64
        ),
        crumb_sizes=np.array((crumb.size for crumb in sim_snapshot.crumbs), np.float64),
        created_at=datetime.fromtimestamp(sim_snapshot.created_at),
    )


def _to_bytes(model: SimSnapshot) -> bytes:
    """
    Serializes a snapshot from a Pydantic model into bytes
    """

    sim_snapshot = simsnapshot_pb2.SimSnapshot()
    sim_snapshot.id = str(model.id)
    sim_snapshot.ant_ids.extend(model.ant_ids.astype(str))

    for position in model.ant_positions:
        ant = sim_snapshot.ants.add()
        ant.x = float(position[0])  # pyright: ignore[reportAny]
        ant.y = float(position[1])  # pyright: ignore[reportAny]

    for i, ant in enumerate(sim_snapshot.ants):
        ant.rotation = float(model.ant_rotations[i])  # pyright: ignore[reportAny]
        ant.pheremone_sensitivity = float(model.ant_pheremone_sensitivities[i])  # pyright: ignore[reportAny]
        ant.pheremone_strength = float(model.ant_pheremone_strengths[i])  # pyright: ignore[reportAny]
        ant.speed = float(model.ant_speeds[i])  # pyright: ignore[reportAny]
        ant.seconds_of_life_left = float(model.ant_seconds_of_life_left[i])  # pyright: ignore[reportAny]

    for crumb_position, crumb_size in zip(model.crumb_positions, model.crumb_sizes):
        crumb = sim_snapshot.crumbs.add()
        crumb.x = float(crumb_position[0])  # pyright: ignore[reportAny]
        crumb.y = float(crumb_position[1])  # pyright: ignore[reportAny]
        crumb.size = float(crumb_size)

    sim_snapshot.created_at = int(model.created_at.timestamp())

    return sim_snapshot.SerializeToString()


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
