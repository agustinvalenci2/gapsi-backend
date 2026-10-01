from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import register_database
from app.routes.auth import router as auth_router
from app.routes.incidents import router as incidents_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with register_database(app):
        yield


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
