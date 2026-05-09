from __future__ import annotations

from pydantic import BaseModel


class CityRead(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class CityCreate(BaseModel):
    name: str
    slug: str
    is_active: bool = True
    sort_order: int = 0


class CityUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryRead(BaseModel):
    slug: str
    title: str
    is_active: bool = True
    sort_order: int


class PartnerRead(BaseModel):
    id: int
    city_id: int
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
    sort_order: int
    city_name: str | None = None
    owner_email: str | None = None

    model_config = {"from_attributes": True}


class PartnerCreate(BaseModel):
    city_id: int
    owner_user_id: int | None = None
    category_slug: str | None = None
    name: str
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    working_hours: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    is_active: bool = True
    is_verified: bool = False
    sort_order: int = 0


class PartnerUpdate(BaseModel):
    city_id: int | None = None
    owner_user_id: int | None = None
    category_slug: str | None = None
    name: str | None = None
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    working_hours: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    sort_order: int | None = None
