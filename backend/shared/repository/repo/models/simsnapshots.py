import uuid
from collections.abc import Mapping
from datetime import datetime

import numpy as np
from pydantic import BaseModel, ConfigDict


class BaseSimSnapshot(BaseModel):
    model_config = ConfigDict(  # pyright: ignore[reportUnannotatedClassAttribute]
        arbitrary_types_allowed=True,
    )

    # all of these ant_ arrays share indexing
    ant_ids: np.ndarray[tuple[int], np.dtype[np.bytes_]]
    ant_positions: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ant_rotations: np.ndarray[tuple[int], np.dtype[np.float64]]
    # TODO: need is_leaving_home bool state

    ant_pheremone_sensitivities: np.ndarray[tuple[int], np.dtype[np.float64]]
    ant_pheremone_strengths: np.ndarray[tuple[int], np.dtype[np.float64]]
    ant_speeds: np.ndarray[tuple[int], np.dtype[np.float64]]
    ant_seconds_of_life_left: np.ndarray[tuple[int], np.dtype[np.float64]]

    # pheremones share indexing
    pheremone_positions: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    pheremone_is_leaving_home: np.ndarray[tuple[int], np.dtype[np.bool]]
    pheremone_seconds_of_life_left: np.ndarray[tuple[int], np.dtype[np.float64]]

    # these crumb_ arrays also share indexing
    crumb_positions: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    crumb_sizes: np.ndarray[tuple[int], np.dtype[np.float64]]


class SimSnapshot(BaseSimSnapshot):
    created_at: datetime

    # for caching!
    _id_to_index: Mapping[uuid.UUID, int] | None = None


class SimSnapshotCreate(BaseSimSnapshot):
    created_at: datetime
