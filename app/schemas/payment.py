from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, TypedDict

from pydantic import BaseModel, Field


class PaymentPayload(TypedDict, total=False):
    data: dict[str, Any]


class PaymentReceiptCreate(BaseModel):
    file_url: str
    uploaded_via: str = "web"


class PaymentReceiptRead(BaseModel):
    id: int
    payment_request_id: int
    file_url: str
    uploaded_via: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentRequestCreate(BaseModel):
    amount: Decimal | None = None
    source: str = "web"
    comment: str | None = None


class PaymentRequestMarkPaid(BaseModel):
    comment: str | None = None


class PaymentRequestRead(BaseModel):
    id: int
    client_id: int
    amount: Decimal
    status: str
    source: str | None
    comment: str | None
    created_at: datetime
    updated_at: datetime | None
    approved_at: datetime | None
    rejected_at: datetime | None
    admin_user_id: int | None
    access_until: datetime | None
    receipts: list[PaymentReceiptRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}
