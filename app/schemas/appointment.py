from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

AppointmentStatusLiteral = Literal["new", "confirmed", "cancelled", "completed", "rejected"]


class _TrimStringsMixin(BaseModel):
    @field_validator("client_name", "client_phone", "comment", "source", mode="before", check_fields=False)
    @classmethod
    def trim_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class PartnerAppointmentCreate(_TrimStringsMixin):
    offer_id: int | None = None
    client_name: str | None = None
    client_phone: str | None = None
    comment: str | None = None
    desired_at: datetime | None = None
    source: str | None = "web"


class PartnerAppointmentStatusUpdate(_TrimStringsMixin):
    status: AppointmentStatusLiteral
    comment: str | None = None


class PartnerAppointmentRead(BaseModel):
    id: int
    client_id: int
    partner_id: int
    partner_name: str | None
    offer_id: int | None
    offer_title: str | None
    status: str
    client_name: str | None
    client_phone: str
    client_email: str | None
    comment: str | None
    desired_at: datetime | None
    source: str | None
    created_at: datetime
    updated_at: datetime | None
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    completed_at: datetime | None
    rejected_at: datetime | None
