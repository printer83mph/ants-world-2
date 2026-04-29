import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import cast

import redis
from repo.impl.simsnapshots import SimSnapshotsRepo
from repo.models.simsnapshots import SimSnapshot

from app import schemas


class SimFetcher:
    @dataclass
    class SnapshotData:
        snapshot: SimSnapshot
        bucketed_ant_idxs: dict[tuple[int, int], list[int]]
        bucketed_crumb_idxs: dict[tuple[int, int], list[int]]

    @dataclass
    class Viewport:
        xmin: float
        ymin: float
        xmax: float
        ymax: float

    def __init__(
        self,
        redis_engine: redis.Redis,
        fetch_interval: float = 8.0,
        fixed_dt: float = 2.0,
    ):
        self.repo: SimSnapshotsRepo = SimSnapshotsRepo(redis_engine=redis_engine)
        self.fetch_interval: float = fetch_interval
        self.fixed_dt: float = (
            fixed_dt  # this should prob be fetched from / shared w the sim service
        )

        self.recent_data: list[SimFetcher.SnapshotData] = []

    def fetch_data(self):
        """
        Fetches recent simulation data from the redis instance.
        This method should be called on the fixed interval configured with `fetch_interval`.
        """

        # we want to collect double the fetch interval's worth of data just in case
        total_snapshots = int(self.fetch_interval * 2 / self.fixed_dt)

        self.recent_data = []
        for snapshot in self.repo.get_last_x(total_snapshots):
            # bucket ants
            bucketed_ant_idxs: dict[tuple[int, int], list[int]] = defaultdict(list)
            for idx, position in enumerate(snapshot.ant_positions):
                bucketed_ant_idxs[
                    self._get_bucket(cast(float, position[0]), cast(float, position[1]))
                ].append(idx)

            # bucket crumbs
            bucketed_crumb_idxs: dict[tuple[int, int], list[int]] = defaultdict(list)
            for idx, position in enumerate(snapshot.crumb_positions):
                bucketed_crumb_idxs[
                    self._get_bucket(cast(float, position[0]), cast(float, position[1]))
                ].append(idx)

            # add all this data to our shit
            self.recent_data.append(
                SimFetcher.SnapshotData(
                    snapshot=snapshot,
                    bucketed_ant_idxs=bucketed_ant_idxs,
                    bucketed_crumb_idxs=bucketed_crumb_idxs,
                )
            )

    def get_viewer_data(
        self, view_time: datetime, viewport: Viewport
    ) -> schemas.WebSocketSimSnapshotMessage | None:
        """
        Compute a snapshot for a given time and viewport.
        Should work as long as we have a steady interval of calling `fetch_data`.
        """

        data = self._get_viewer_snapshot_data(view_time)

        if data is None:
            return None

        shown_ant_idxs: list[int] = []
        shown_crumb_idxs: list[int] = []

        # grab everything in relevant buckets
        xbmin, ybmin = self._get_bucket(viewport.xmin, viewport.ymin)
        xbmax, ybmax = self._get_bucket(viewport.xmax, viewport.ymax)
        for x in range(xbmin, xbmax):
            for y in range(ybmin, ybmax):
                if (x, y) in data.bucketed_ant_idxs:
                    shown_ant_idxs.extend(data.bucketed_ant_idxs[(x, y)])
                if (x, y) in data.bucketed_crumb_idxs:
                    shown_crumb_idxs.extend(data.bucketed_crumb_idxs[(x, y)])

        return schemas.WebSocketSimSnapshotMessage(
            created_at=data.snapshot.created_at,
            ants=[
                schemas.SnapshotAnt(
                    position=(
                        data.snapshot.ant_positions[i][0],
                        data.snapshot.ant_positions[i][1],
                    ),
                    rotation=cast(float, data.snapshot.ant_rotations[i]),
                )
                for i in shown_ant_idxs
            ],
            crumbs=[
                schemas.SnapshotCrumb(
                    position=(
                        data.snapshot.crumb_positions[i][0],
                        data.snapshot.crumb_positions[i][1],
                    ),
                    size=cast(float, data.snapshot.crumb_sizes[i]),
                )
                for i in shown_crumb_idxs
            ],
        )

    BUCKET_SIZE: float = 2.0

    def _get_bucket(self, x: float, y: float) -> tuple[int, int]:
        return (
            math.floor(x / SimFetcher.BUCKET_SIZE),
            math.floor(y / SimFetcher.BUCKET_SIZE),
        )

    def _get_viewer_snapshot_data(self, view_time: datetime) -> SnapshotData | None:
        # go back by fetch interval since we have double the interval buffered
        query_time = view_time - timedelta(seconds=self.fetch_interval)

        # grab the fist snapshot which is older than query time
        for data in self.recent_data:
            if data.snapshot.created_at < query_time:
                return data

        return None
