import random
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timezone

import numpy as np
import redis
from repo.impl.simsnapshots import SimSnapshotsRepo
from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate


class Simulator:
    def __init__(self, redis_connection_url: str):
        redis_engine = redis.Redis(redis_connection_url, decode_responses=True)
        self.repo = SimSnapshotsRepo(redis_engine)

        # attempt to fetch last snapshot
        last_snapshots = self.repo.get_last_x(1)

        # seed snapshot if not exists (empty)
        if len(last_snapshots) == 0:
            self.last_snapshot = SimSnapshot(
                created_at=datetime.now(tz=timezone.utc),
                ant_ids=np.array([], np.bytes_),
                ant_positions=np.array([], np.float64),
                ant_rotations=np.array([], np.float64),
                ant_pheremone_sensitivities=np.array([], np.float64),
                ant_pheremone_strengths=np.array([], np.float64),
                ant_speeds=np.array([], np.float64),
                ant_seconds_of_life_left=np.array([], np.float64),
                pheremone_positions=np.array([], np.float64),
                pheremone_is_leaving_home=np.array([], np.bool),
                pheremone_seconds_of_life_left=np.array([], np.float64),
                crumb_positions=np.array([], np.float64),
                crumb_sizes=np.array([], np.float64),
            )
        else:
            self.last_snapshot = last_snapshots[0]

    # optimization
    BUCKET_SIZE: float = 0.5  # meters

    def _get_bucket(self, x: float, y: float) -> tuple[int, int]:
        return (
            np.floor(x / Simulator.BUCKET_SIZE),
            np.floor(y / Simulator.BUCKET_SIZE),
        )

    def _nearby_buckets(
        self, x: float, y: float, radius: float
    ) -> Iterator[tuple[int, int]]:
        x_min, y_min = self._get_bucket(x - radius, y - radius)
        x_max, y_max = self._get_bucket(x + radius, y + radius)

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                yield (x, y)

    def tick(self, dt: float = 1.0):
        snapshot = self.last_snapshot

        bucketed_crumb_idxs: dict[tuple[int, int], list[int]] = defaultdict(list)
        for idx, (x, y) in enumerate(snapshot.crumb_positions):
            bucketed_crumb_idxs[self._get_bucket(x, y)].append(idx)

        bucketed_pheremone_idxs: dict[tuple[int, int], list[int]] = defaultdict(list)
        for idx, (x, y) in enumerate(snapshot.pheremone_positions):
            bucketed_pheremone_idxs[self._get_bucket(x, y)].append(idx)

        new_crumb_sizes = np.copy(snapshot.crumb_sizes)

        ant_ids: list[bytes] = []
        ant_positions: list[tuple[float, float]] = []
        ant_rotations: list[float] = []
        ant_pheremone_sensitivities: list[float] = []
        ant_pheremone_strengths: list[float] = []
        ant_speeds: list[float] = []
        ant_seconds_of_life_left: list[float] = []

        for ant_idx in range(len(snapshot.ant_ids)):
            ant_id = snapshot.ant_ids[ant_idx]
            x, y = snapshot.ant_positions[ant_idx]
            rotation = snapshot.ant_rotations[ant_idx]
            pheremone_sensitivity = snapshot.ant_pheremone_sensitivities[ant_idx]
            pheremone_strength = snapshot.ant_pheremone_strengths[ant_idx]
            speed = snapshot.ant_speeds[ant_idx]
            seconds_of_life_left = snapshot.ant_seconds_of_life_left[ant_idx]

            # get nearby bucketed pheremones
            nearby_pheremone_idxs = []
            for bucket in self._nearby_buckets(x, y, pheremone_sensitivity):
                nearby_pheremone_idxs.extend(bucketed_pheremone_idxs[bucket])

            # get nearby crumbs
            nearby_crumb_idxs = []
            for bucket in self._nearby_buckets(x, y, pheremone_sensitivity):
                nearby_crumb_idxs.extend(bucketed_crumb_idxs[bucket])

            random_rotation = (random.random() - 0.5) * 10
            new_rotation = rotation + random_rotation

            new_x, new_y = (
                x + np.cos(new_rotation) * speed * dt,
                y + np.sin(new_rotation) * speed * dt,
            )

            if seconds_of_life_left - dt > 0:
                ant_ids.append(ant_id)
                ant_positions.append((new_x, new_y))
                ant_rotations.append(new_rotation)
                ant_pheremone_sensitivities.append(pheremone_sensitivity)
                ant_pheremone_strengths.append(pheremone_strength)
                ant_speeds.append(speed)
                ant_seconds_of_life_left.append(seconds_of_life_left - dt)

        # remove deleted pheremones
        new_pheremone_seconds_left = snapshot.pheremone_seconds_of_life_left - dt
        pheremone_mask = new_pheremone_seconds_left > 0

        # remove deleted crumbs
        crumb_mask = new_crumb_sizes > 0

        self.repo.publish(
            SimSnapshotCreate(
                created_at=datetime.now(tz=timezone.utc),
                #
                # ants
                ant_ids=np.array(ant_ids, np.bytes_),
                ant_positions=np.array(ant_positions, np.float64),
                ant_rotations=np.array(ant_rotations, np.float64),
                ant_pheremone_sensitivities=np.array(
                    ant_pheremone_sensitivities, np.float64
                ),
                ant_pheremone_strengths=np.array(ant_pheremone_strengths, np.float64),
                ant_speeds=np.array(ant_speeds, np.float64),
                ant_seconds_of_life_left=np.array(ant_seconds_of_life_left, np.float64),
                #
                # pheremones
                pheremone_positions=snapshot.pheremone_positions[pheremone_mask],
                pheremone_is_leaving_home=snapshot.pheremone_is_leaving_home[
                    pheremone_mask
                ],
                pheremone_seconds_of_life_left=new_pheremone_seconds_left,
                #
                # crumbs
                crumb_positions=snapshot.crumb_positions[crumb_mask],
                crumb_sizes=snapshot.crumb_sizes[crumb_mask],
            )
        )
