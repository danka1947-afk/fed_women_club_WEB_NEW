from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VerificationRequest:
    id: int | None
    user_id: int
    status: str
