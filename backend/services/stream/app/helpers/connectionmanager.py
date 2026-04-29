import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import WebSocket

from app.helpers.simfetcher import SimFetcher
from app.schemas import WebSocketSetViewportClientMessage


@dataclass
class Connection:
    websocket: WebSocket
    viewport: SimFetcher.Viewport | None = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, Connection] = {}

    async def connect(self, websocket: WebSocket, id: uuid.UUID):
        await websocket.accept()
        self.active_connections[id] = Connection(websocket=websocket)

    def disconnect(self, id: uuid.UUID):
        del self.active_connections[id]

    async def set_viewport(
        self,
        id: uuid.UUID,
        request: WebSocketSetViewportClientMessage,
        simfetcher: SimFetcher,
    ) -> None:
        """
        Set the viewport for a specific connection
        """

        connection = self.active_connections[id]
        connection.viewport = SimFetcher.Viewport(
            xmin=request.xmin, xmax=request.xmax, ymin=request.ymin, ymax=request.ymax
        )

        # also update client data
        view_time = datetime.now(tz=timezone.utc)
        await self._try_send_viewer_snapshot(connection, simfetcher, view_time)

    async def broadcast_snapshots(self, simfetcher: SimFetcher):
        """
        Send out regular interval snapshots to all active connections
        """

        view_time = datetime.now(tz=timezone.utc)
        _ = await asyncio.gather(
            *[
                self._try_send_viewer_snapshot(connection, simfetcher, view_time)
                for connection in self.active_connections.values()
            ]
        )

    async def _try_send_viewer_snapshot(
        self, connection: Connection, simfetcher: SimFetcher, view_time: datetime
    ):
        # skip if viewport not set up
        if connection.viewport is None:
            return

        snapshot = simfetcher.get_viewer_data(view_time, connection.viewport)
        if snapshot is None:
            return

        # send the client the snapshot!
        await connection.websocket.send_text(snapshot.model_dump_json())


connectionmanager = ConnectionManager()
