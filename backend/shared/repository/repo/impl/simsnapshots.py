import uuid
from collections.abc import Iterator, Sequence
from datetime import datetime, timezone
from typing import cast, override

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


REDIS_LIST = "simsnapshots"
REDIS_PUBSUB = "simsnapshots"


class SimSnapshotsRepo(abstract.SimSnapshotsRepo):
    def __init__(self, redis_engine: redis.Redis):
        self.redis: redis.Redis = redis_engine

    @override
    def publish(self, create: SimSnapshotCreate) -> SimSnapshot:
        created_at = datetime.now(tz=timezone.utc)
        full_snapshot = SimSnapshot(
            created_at=created_at,
            **create.__dict__,  # pyright: ignore[reportAny]
        )

        serialized = _to_bytes(full_snapshot)

        # add to list and publish!
        _ = self.redis.lpush(REDIS_LIST, serialized)
        _ = self.redis.publish(REDIS_PUBSUB, serialized)
        if cast(int, self.redis.llen(REDIS_LIST)) > 20:
            # save last 30 snapshots, discard older ones
            self.redis.lpop(REDIS_LIST, 1)

        return full_snapshot

    @override
    def subscribe(self) -> Iterator[SimSnapshot]:
        p = self.redis.pubsub()
        p.subscribe(REDIS_PUBSUB)

        try:
            for message in p.listen():
                assert isinstance(message["data"], bytes)
                yield _to_model(cast(bytes, message["data"]))

        finally:
            p.unsubscribe(REDIS_PUBSUB)

    @override
    def get_last_x(self, count: int) -> Sequence[SimSnapshot]:
        serialized_snapshots = cast(
            list[bytes],
            self.redis.lrange(REDIS_LIST, 0, count - 1),
        )
        return [_to_model(snapshot) for snapshot in serialized_snapshots]

    @override
    def get_ant_index_by_id(self, snapshot: SimSnapshot, id: uuid.UUID) -> int | None:
        if snapshot._id_to_index is None:  # pyright: ignore[reportPrivateUsage]
            snapshot._id_to_index = dict(  # pyright: ignore[reportPrivateUsage]
                (uuid.UUID(bytes=ant_id_bytes), idx)
                for idx, ant_id_bytes in enumerate(snapshot.ant_ids)
            )

        return snapshot._id_to_index.get(id, None)  # pyright: ignore[reportPrivateUsage]
