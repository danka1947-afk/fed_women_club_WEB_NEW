from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UserRole(StrEnum):
    admin = "admin"
    partner = "partner"
    client = "client"


@dataclass(slots=True)
class User:
    id: int | None
    email: str
    role: UserRole
    is_active: bool = True
