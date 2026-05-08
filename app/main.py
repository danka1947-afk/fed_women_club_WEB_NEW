from __future__ import annotations

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
