from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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
    instagram_url: str | None
    vk_url: str | None
    telegram_url: str | None
    whatsapp_url: str | None
    map_url: str | None
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
    instagram_url: str | None = None
    vk_url: str | None = None
    telegram_url: str | None = None
    whatsapp_url: str | None = None
    map_url: str | None = None
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


class PartnerPhotoRead(BaseModel):
    id: int
    partner_id: int
    url: str
    alt_text: str | None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PartnerPhotoUpdate(BaseModel):
    alt_text: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class PartnerPhotoUploadResponse(PartnerPhotoRead):
    pass


class OfferPhotoRead(BaseModel):
    id: int
    offer_id: int
    url: str
    alt_text: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OfferPhotoUpdate(BaseModel):
    alt_text: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class PartnerAnalyticsRead(BaseModel):
    partner_id: int
    partner_name: str | None = None
    qr_links_count: int
    lead_clicks_count: int
    privileges_created_count: int
    privileges_confirmed_count: int
    active_privileges_count: int
    expired_privileges_count: int
    conversion_to_privilege_percent: float
    confirmation_rate_percent: float


class PartnerVerificationRead(BaseModel):
    id: int
    client_id: int
    client_name: str | None
    partner_id: int
    partner_name: str | None
    offer_id: int | None
    offer_title: str | None
    code: str
    status: str
    source: str | None
    expires_at: datetime
    confirmed_at: datetime | None
    created_at: datetime
    ttl_seconds: int | None


class ConfirmVerificationResponse(BaseModel):
    id: int
    status: str
    confirmed_at: datetime | None


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


class PublicLandingPartnerOffer(BaseModel):
    title: str
    discount_text: str | None
    description: str | None
    terms: str | None


class PublicLandingPartnerPhoto(BaseModel):
    id: int
    url: str
    alt_text: str | None
    sort_order: int


class PublicLandingPartnerCard(BaseModel):
    id: int
    name: str
    address: str | None
    city_name: str
    city_slug: str
    category_title: str
    category_slug: str
    logo_url: str | None
    cover_url: str | None
    offers: list[PublicLandingPartnerOffer]
    photos: list[PublicLandingPartnerPhoto] = Field(default_factory=list)


class PublicLandingPartnerListResponse(BaseModel):
    items: list[PublicLandingPartnerCard]
