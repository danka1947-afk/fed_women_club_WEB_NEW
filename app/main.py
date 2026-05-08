from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings


@dataclass(slots=True)
class Route:
    path: str
    endpoint: Callable[..., Any]
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SkeletonApp:
    title: str
    routes: list[Route] = field(default_factory=list)

    def get(self, path: str, *, tags: list[str] | None = None):
        def decorator(endpoint: Callable[..., Any]) -> Callable[..., Any]:
            self.routes.append(Route(path=path, endpoint=endpoint, tags=tags or []))
            return endpoint

        return decorator


app = SkeletonApp(title=settings.PROJECT_NAME)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
