from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PaymentRequestStatus(StrEnum):
    pending = "pending"
    paid = "paid"
    approved = "approved"
    rejected = "rejected"


@dataclass(slots=True)
class PaymentRequest:
    id: int | None
    client_user_id: int
    status: PaymentRequestStatus
    created_at: datetime | None = None
