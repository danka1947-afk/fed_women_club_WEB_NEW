from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SkeletonRouter:
    prefixes: list[str] = field(default_factory=list)

    def include_router(self, router: "SkeletonRouter", *, prefix: str = "") -> None:
        self.prefixes.append(prefix)


api_router = SkeletonRouter()
