from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClientProfile:
    id: int | None
    user_id: int
    city_code: str
