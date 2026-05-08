from __future__ import annotations

from typing import Any, TypedDict


class AuthPayload(TypedDict, total=False):
    data: dict[str, Any]
