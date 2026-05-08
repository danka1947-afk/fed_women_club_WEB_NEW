from __future__ import annotations

from typing import Any, TypedDict


class VkPayload(TypedDict, total=False):
    data: dict[str, Any]
