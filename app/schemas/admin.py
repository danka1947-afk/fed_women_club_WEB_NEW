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
