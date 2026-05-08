from __future__ import annotations


def require_role(*roles: str):
    def dependency() -> tuple[str, ...]:
        return roles

    return dependency
