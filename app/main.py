from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.endpoints.public import router as public_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
)

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.PUBLIC_UPLOADS_PATH, StaticFiles(directory=upload_dir), name="uploads")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(public_router)
app.include_router(api_router)
