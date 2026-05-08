from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class LeadClick:
    id: int | None
    qr_link_id: int
    visitor_id: str
    clicked_at: datetime
