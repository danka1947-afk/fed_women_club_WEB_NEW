from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.categories import get_women_club_categories
from app.db.session import get_db
from app.models.city import City
from app.models.user import AdminUser
from app.schemas.admin import CategoryRead, CityCreate, CityRead, CityUpdate
from app.schemas.auth import AdminUserRead

router = APIRouter(prefix="/admin", tags=["admin"])

CITY_DUPLICATE_DETAIL = "City with this slug or name already exists"


@router.get("/me", response_model=AdminUserRead)
def read_admin_me(admin: AdminUser = Depends(require_admin)) -> AdminUser:
    return admin


@router.get("/cities", response_model=list[CityRead])
def list_admin_cities(
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[City]:
    _ = admin
    result = db.execute(select(City).order_by(City.sort_order.asc(), City.id.asc()))
    return list(result.scalars().all())


@router.post("/cities", response_model=CityRead)
def create_admin_city(
    payload: CityCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> City:
    _ = admin
    name = _strip_required(payload.name, "name")
    slug = _strip_required(payload.slug, "slug")
    _ensure_unique_city_identity(db, name=name, slug=slug)

    city = City(name=name, slug=slug, is_active=payload.is_active, sort_order=payload.sort_order)
    db.add(city)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _city_duplicate_error() from None
    db.refresh(city)
    return city


@router.patch("/cities/{city_id}", response_model=CityRead)
def update_admin_city(
    city_id: int,
    payload: CityUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> City:
    _ = admin
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    update_data = payload.model_dump(exclude_unset=True)
    next_name = _strip_required(update_data["name"], "name") if "name" in update_data else city.name
    next_slug = _strip_required(update_data["slug"], "slug") if "slug" in update_data else city.slug
    _ensure_unique_city_identity(db, name=next_name, slug=next_slug, exclude_city_id=city.id)

    for field, value in update_data.items():
        if field == "name":
            city.name = next_name
        elif field == "slug":
            city.slug = next_slug
        elif field == "is_active":
            city.is_active = value
        elif field == "sort_order":
            city.sort_order = value

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _city_duplicate_error() from None
    db.refresh(city)
    return city


@router.get("/categories", response_model=list[CategoryRead])
def list_admin_categories(admin: AdminUser = Depends(require_admin)) -> list[dict[str, object]]:
    _ = admin
    return sorted(get_women_club_categories(), key=lambda category: category["sort_order"])


def _strip_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"City {field_name} must not be empty",
        )
    return normalized


def _ensure_unique_city_identity(
    db: Session,
    *,
    name: str,
    slug: str,
    exclude_city_id: int | None = None,
) -> None:
    statement = select(City.id).where(or_(City.name == name, City.slug == slug))
    if exclude_city_id is not None:
        statement = statement.where(City.id != exclude_city_id)
    duplicate_id = db.execute(statement.limit(1)).scalar_one_or_none()
    if duplicate_id is not None:
        raise _city_duplicate_error()


def _city_duplicate_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=CITY_DUPLICATE_DETAIL)
