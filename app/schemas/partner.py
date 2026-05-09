from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class PartnerProfileRead(BaseModel):
    id: int
    city_id: int
    city_name: str | None
    owner_user_id: int | None
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
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class PartnerProfileUpdate(BaseModel):
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    working_hours: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None


class PartnerOfferRead(BaseModel):
    id: int
    partner_id: int
    title: str
    description: str | None
    benefit_text: str | None
    conditions: str | None
    base_price: Decimal | None
    discount_percent: Decimal | None
    image_url: str | None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class PartnerOfferCreate(BaseModel):
    title: str
    description: str | None = None
    benefit_text: str | None = None
    conditions: str | None = None
    base_price: Decimal | None = None
    discount_percent: Decimal | None = None
    image_url: str | None = None
    is_active: bool = True
    sort_order: int = 0


class PartnerOfferUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    benefit_text: str | None = None
    conditions: str | None = None
    base_price: Decimal | None = None
    discount_percent: Decimal | None = None
    image_url: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None

class PartnerQrLinkRead(BaseModel):
    id: int
    partner_id: int
    slug: str
    deep_link_payload: str | None
    target_url: str | None
    is_active: bool
    qr_url: str
    partner_name: str | None = None

    model_config = {"from_attributes": True}


class LeadStatsRead(BaseModel):
    partner_id: int
    partner_name: str
    city_id: int | None
    city_name: str | None
    qr_link_id: int | None
    qr_slug: str | None
    total_clicks: int
