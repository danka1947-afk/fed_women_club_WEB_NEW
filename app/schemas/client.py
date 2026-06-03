from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ClientProfileRead(BaseModel):
    id: int
    user_id: int
    email: str | None
    phone: str | None
    contact_email: str | None
    full_name: str | None
    selected_city_id: int | None
    selected_city_name: str | None
    city: str | None = None
    custom_city: str | None = None
    city_name: str | None = None
    vk_user_id: str | None
    site_login: str | None = None
    site_password_masked: str | None = None
    site_password_available: bool = False
    source: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class ClientSiteCredentialsRead(BaseModel):
    site_login: str
    site_password: str


class ClientProfileUpdate(BaseModel):
    name: str | None = None
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    contact_email: str | None = None
    city_id: int | None = None
    city_slug: str | None = None
    selected_city_id: int | None = None
    city: str | None = None
    custom_city: str | None = None


class ClientCityResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class SubscriptionRead(BaseModel):
    id: int | None = None
    client_id: int | None = None
    status: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    source_payment_request_id: int | None = None
    is_active: bool
    expires_at: datetime | None = None
    end_date: datetime | None = None
    amount: Decimal = Decimal("349.00")

    model_config = {"from_attributes": True}


class ClientPartnerPhotoRead(BaseModel):
    id: int
    url: str
    alt_text: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientPartnerCatalogItem(BaseModel):
    id: int
    city_id: int
    city_name: str | None
    category_id: int | None = None
    category_name: str | None = None
    category_slug: str | None
    category: "ClientPartnerCategoryRead | None" = None
    categories: list["ClientPartnerCategoryRead"] = Field(default_factory=list)
    category_ids: list[int] = Field(default_factory=list)
    category_slugs: list[str] = Field(default_factory=list)
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
    photo_url: str | None = None
    is_verified: bool
    photos: list[ClientPartnerPhotoRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ClientPartnerCategoryRead(BaseModel):
    id: int
    name: str
    slug: str


class ClientCreateVerificationRequest(BaseModel):
    offer_id: int | None = None
    source: str | None = "web"


class ClientVerificationRead(BaseModel):
    id: int
    session_id: int | None = None
    client_id: int
    partner_id: int
    partner_name: str | None
    offer_id: int | None
    offer_title: str | None
    code: str
    display_code: str | None = None
    token: str | None = None
    qr_payload: str | None = None
    status: str
    source: str | None
    expires_at: datetime
    confirmed_at: datetime | None
    created_at: datetime
    ttl_seconds: int | None
    subscription_required: bool = False


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
    photo_url: str | None = None
    photos: list["ClientOfferPhotoRead"] = Field(default_factory=list)
    sort_order: int

    model_config = {"from_attributes": True}


class ClientOfferPhotoRead(BaseModel):
    id: int
    url: str
    alt_text: str | None
    sort_order: int


class ClientSavingsItemRead(BaseModel):
    id: int
    used_at: datetime | None
    partner_id: int
    partner_name: str | None
    offer_id: int | None
    offer_title: str | None
    base_price: Decimal | None
    final_price: Decimal | None
    discount_percent: Decimal | None
    saving_amount: Decimal


class ClientSavingsPeriodRead(BaseModel):
    from_date: str | None
    to_date: str | None


class ClientSavingsRead(BaseModel):
    total_saving_amount: Decimal
    currency: str = "RUB"
    period: ClientSavingsPeriodRead
    items: list[ClientSavingsItemRead]
