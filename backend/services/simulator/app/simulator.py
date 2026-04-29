import logging
import random
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timezone

import numpy as np
import redis
from repo.impl.simsnapshots import SimSnapshotsRepo
from repo.models.simsnapshots import SimSnapshot, SimSnapshotCreate


class Simulator:
    def __init__(self, *, redis_url: str):
        redis_engine = redis.from_url(redis_url)
        self.repo = SimSnapshotsRepo(redis_engine)

        # attempt to fetch last snapshot
        last_snapshots = self.repo.get_last_x(1)

        # seed snapshot if not exists (empty)
        if len(last_snapshots) == 0:
            logging.debug("Last snapshot not found! Initializing empty arrays.")
            self.last_snapshot = SimSnapshot(
                created_at=datetime.now(tz=timezone.utc),
                ant_ids=np.array([], np.bytes_),
                ant_positions=np.empty((0, 2), dtype=np.float64),
                ant_rotations=np.array([], np.float64),
                ant_pheremone_sensitivities=np.array([], np.float64),
                ant_pheremone_strengths=np.array([], np.float64),
                ant_speeds=np.array([], np.float64),
                ant_seconds_of_life_left=np.array([], np.float64),
                pheremone_positions=np.empty((0, 2), dtype=np.float64),
                pheremone_is_leaving_home=np.array([], np.bool_),
                pheremone_seconds_of_life_left=np.array([], np.float64),
                crumb_positions=np.empty((0, 2), dtype=np.float64),
                crumb_sizes=np.array([], np.float64),
            )
        else:
            logging.debug(
                f"Loading from last snapshot, at time {last_snapshots[0].created_at.isoformat()}"
            )
            self.last_snapshot = last_snapshots[0]

    # optimization
    BUCKET_SIZE: float = 0.5  # meters

    def _get_bucket(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(np.floor(x / Simulator.BUCKET_SIZE)),
            int(np.floor(y / Simulator.BUCKET_SIZE)),
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

            random_rotation = (random.random() - 0.5) * 2
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

        # generate new crumb if under threshold
        added_crumb_positions: list[tuple[float, float]] = []
        added_crumb_sizes: list[float] = []
        if len(snapshot.crumb_positions) < 10:
            added_crumb_positions.append((random.random() * 10, random.random() * 10))
            added_crumb_sizes.append(random.random() * 5)

        # Concatenate crumb positions (handle 2D arrays properly)
        existing_crumbs = snapshot.crumb_positions[crumb_mask]
        if added_crumb_positions:
            new_crumb_positions = np.vstack(
                [existing_crumbs, np.array(added_crumb_positions, dtype=np.float64)]
            )
        else:
            new_crumb_positions = existing_crumbs

        # Concatenate crumb sizes (handle 1D arrays properly)
        existing_crumb_sizes = snapshot.crumb_sizes[crumb_mask]
        if added_crumb_sizes:
            new_crumb_sizes_array = np.concatenate(
                [existing_crumb_sizes, np.array(added_crumb_sizes, dtype=np.float64)]
            )
        else:
            new_crumb_sizes_array = existing_crumb_sizes

        new_snapshot = self.repo.publish(
            SimSnapshotCreate(
                created_at=datetime.now(tz=timezone.utc),
                #
                # ants
                ant_ids=np.array(ant_ids, np.bytes_),
                ant_positions=np.array(ant_positions, dtype=np.float64)
                if ant_positions
                else np.empty((0, 2), dtype=np.float64),
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
                pheremone_seconds_of_life_left=new_pheremone_seconds_left[
                    pheremone_mask
                ],
                #
                # crumbs
                crumb_positions=new_crumb_positions,
                crumb_sizes=new_crumb_sizes_array,
            )
        )

        # replace our last snapshot!
        self.last_snapshot = new_snapshot
        logging.debug(f"Published new snapshot: {new_snapshot}")
