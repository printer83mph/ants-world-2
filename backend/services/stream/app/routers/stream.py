import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from typing import cast

import redis
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.config import settings
from app.helpers.connectionmanager import connectionmanager
from app.helpers.simfetcher import SimFetcher
from app.schemas import WebSocketClientMessage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create singleton resource
    redis_engine = redis.from_url(settings.redis_url)
    simfetcher = SimFetcher(
        redis_engine=redis_engine,
        fetch_interval=settings.fixed_dt * 3,  # provide some buffer
        fixed_dt=settings.fixed_dt,
    )
    app.state.simfetcher = simfetcher

    async def fetch_data():
        while True:
            simfetcher.fetch_data()
            await asyncio.sleep(settings.fixed_dt)

    async def broadcast_snapshots():
        while True:
            _ = await connectionmanager.broadcast_snapshots(simfetcher)
            await asyncio.sleep(settings.fixed_dt)

    # we start this background task runnin!
    logging.info("starting data fetching task...")
    _ = asyncio.create_task(fetch_data())
    logging.info("starting snapshot broadcasting task...")
    _ = asyncio.create_task(broadcast_snapshots())

    yield

    # Shutdown: Clean up stuffs
    redis_engine.close()


router = APIRouter(tags=["streaming"], lifespan=lifespan)


@router.websocket("/ws")
async def join_stream(websocket: WebSocket):
    simfetcher = cast(SimFetcher, websocket.app.state.simfetcher)  # pyright: ignore[reportAny]

    # unique id for this connection
    id = uuid.uuid4()

    await connectionmanager.connect(websocket, id)
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                message = WebSocketClientMessage.model_validate_json(raw_data)
                match message.request.type:
                    case "set-viewport":
                        await connectionmanager.set_viewport(
                            id, message.request, simfetcher
                        )

            except ValidationError:
                pass  # LOL we don't care

    except WebSocketDisconnect:
        connectionmanager.disconnect(id)
