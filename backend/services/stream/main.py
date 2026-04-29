from fastapi import FastAPI

from app import schemas
from app.config import settings
from app.routers.stream import router as stream_router

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def healthcheck() -> schemas.BaseResponse:
    return schemas.BaseResponse(message="I'm healthy!")


app.include_router(stream_router)
