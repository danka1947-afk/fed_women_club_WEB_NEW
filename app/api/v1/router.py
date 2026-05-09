from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, bot_vk, clients, partners

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(partners.router)
api_router.include_router(clients.router)
api_router.include_router(bot_vk.router)
