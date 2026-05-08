from __future__ import annotations

from typing import Any, TypedDict


class PartnerPayload(TypedDict, total=False):
    data: dict[str, Any]
