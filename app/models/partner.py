from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Partner:
    id: int | None
    city_code: str
    name: str
    is_active: bool = True


@dataclass(slots=True)
class PartnerQrLink:
    id: int | None
    partner_id: int
    slug: str
    target_url: str | None = None
    is_active: bool = True
