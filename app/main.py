from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.endpoints.public import router as public_router
from app.api.v1.endpoints.auth import router as root_auth_router


logger = logging.getLogger("app.auth_cors")

VK_MINIAPP_AUTH_LOG_PATHS = {"/api/v1/auth/vk-miniapp-login", "/auth/vk-miniapp-login"}


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins_list,
    allow_origin_regex=r"https://([a-z0-9-]+\.)*(vk\.ru|vk\.com|bloomclub\.ru)$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.PUBLIC_UPLOADS_PATH, StaticFiles(directory=upload_dir), name="uploads")

vk_mini_app_dir = Path("app/static/vk-mini-app")


def _vk_mini_app_path(relative_path: str) -> Path:
    candidate = (vk_mini_app_dir / relative_path).resolve()
    base = vk_mini_app_dir.resolve()
    if base not in candidate.parents and candidate != base:
        raise HTTPException(status_code=404, detail="Not found")
    return candidate


def _vk_mini_app_index() -> FileResponse:
    index_path = vk_mini_app_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=503,
            detail="VK Mini App build is not deployed. Place build files into app/static/vk-mini-app/",
        )
    return FileResponse(index_path)


@app.get("/vk-mini-app/")
async def vk_mini_app_entrypoint() -> FileResponse:
    return _vk_mini_app_index()


@app.get("/vk-mini-app/{full_path:path}")
async def vk_mini_app_static(full_path: str) -> FileResponse:
    if not full_path:
        return _vk_mini_app_index()

    file_path = _vk_mini_app_path(full_path)
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    return _vk_mini_app_index()


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(public_router)
app.include_router(api_router)
app.include_router(root_auth_router)


@app.middleware("http")
async def log_vk_miniapp_auth_cors_debug(request, call_next):
    path = request.url.path
    if path not in VK_MINIAPP_AUTH_LOG_PATHS:
        return await call_next(request)

    method = request.method
    origin = request.headers.get("origin", "")
    acr_method = request.headers.get("access-control-request-method", "")
    acr_headers = request.headers.get("access-control-request-headers", "")
    user_agent = request.headers.get("user-agent", "")[:120]

    response = await call_next(request)
    logger.info(
        "vk-miniapp-login method=%s path=%s origin=%s acr_method=%s acr_headers=%s status=%s ua=%s",
        method,
        path,
        origin,
        acr_method,
        acr_headers,
        response.status_code,
        user_agent,
    )
    return response
