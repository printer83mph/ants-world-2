from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    message: str | None = None


# client-to-server stuff


class WebSocketSetViewportClientMessage(BaseModel):
    type: Literal["set-viewport"] = "set-viewport"
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class WebSocketClientMessage(BaseModel):
    request: WebSocketSetViewportClientMessage = Field(discriminator="type")


# server-to-client stuff


class SnapshotAnt(BaseModel):
    position: tuple[float, float]
    rotation: float


class SnapshotCrumb(BaseModel):
    position: tuple[float, float]
    size: float


class WebSocketSimSnapshotMessage(BaseModel):
    created_at: datetime
    ants: list[SnapshotAnt]
    crumbs: list[SnapshotCrumb]
