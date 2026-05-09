from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ClientProfileRead(BaseModel):
    id: int
    user_id: int
    email: str | None
    phone: str | None
    full_name: str | None
    selected_city_id: int | None
    selected_city_name: str | None
    vk_user_id: str | None
    source: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class ClientProfileUpdate(BaseModel):
    full_name: str | None = None
    selected_city_id: int | None = None


class SubscriptionRead(BaseModel):
    id: int
    client_id: int
    status: str
    starts_at: datetime
    ends_at: datetime
    source_payment_request_id: int | None

    model_config = {"from_attributes": True}


class ClientPartnerCatalogItem(BaseModel):
    id: int
    city_id: int
    city_name: str | None
    category_slug: str | None
    name: str
    description: str | None
    address: str | None
    phone: str | None
    website_url: str | None
    social_url: str | None
    working_hours: str | None
    logo_url: str | None
    cover_url: str | None
    is_verified: bool

    model_config = {"from_attributes": True}


class ClientPartnerOfferRead(BaseModel):
    id: int
    partner_id: int
    title: str
    description: str | None
    benefit_text: str | None
    conditions: str | None
    base_price: Decimal | None
    discount_percent: Decimal | None
    image_url: str | None
    sort_order: int

    model_config = {"from_attributes": True}
