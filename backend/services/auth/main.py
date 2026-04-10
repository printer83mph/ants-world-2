from fastapi import FastAPI

from app import schemas
from app.config import settings
from app.routers.auth import router as auth_router

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def healthcheck() -> schemas.BaseResponse:
    return schemas.BaseResponse(message="I'm healthy!")


app.include_router(auth_router)
