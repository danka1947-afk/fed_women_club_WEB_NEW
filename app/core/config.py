from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Federal Women Club WEB")
    ENV: str = os.getenv("ENV", "test")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-test-secret")
    BOT_SERVICE_TOKEN: str = os.getenv("BOT_SERVICE_TOKEN", "change-me-test-token")
    LEAD_HASH_SALT: str = os.getenv("LEAD_HASH_SALT", "change-me-test-salt")
    BACKEND_CORS_ORIGINS: str = os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    WEB_PUBLIC_URL: str = os.getenv("WEB_PUBLIC_URL", "https://women-club.example")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    PUBLIC_UPLOADS_PATH: str = os.getenv("PUBLIC_UPLOADS_PATH", "/uploads")

    @property
    def backend_cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def visitor_cookie_secure(self) -> bool:
        return self.ENV.lower() in {"production", "prod", "staging"}


settings = Settings()
