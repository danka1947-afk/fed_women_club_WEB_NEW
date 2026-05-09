from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.categories import WOMEN_CLUB_CATEGORY_SLUGS, get_women_club_categories
from app.db.session import get_db
from app.models.city import City
from app.models.partner import Partner, PartnerOffer
from app.models.user import AdminUser, User, UserRole
from app.schemas.admin import (
    CategoryRead,
    CityCreate,
    CityRead,
    CityUpdate,
    PartnerCreate,
    PartnerOfferCreate,
    PartnerOfferRead,
    PartnerOfferUpdate,
    PartnerRead,
    PartnerUpdate,
)
from app.schemas.auth import AdminUserRead

router = APIRouter(prefix="/admin", tags=["admin"])

CITY_DUPLICATE_DETAIL = "City with this slug or name already exists"
PARTNER_TEXT_FIELDS = (
    "description",
    "address",
    "phone",
    "website_url",
    "social_url",
    "working_hours",
    "logo_url",
    "cover_url",
)
PARTNER_OFFER_TEXT_FIELDS = ("description", "benefit_text", "conditions", "image_url")


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


@router.get("/partners", response_model=list[PartnerRead])
def list_admin_partners(
    city_id: int | None = None,
    is_active: bool | None = None,
    category_slug: str | None = None,
    q: str | None = None,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PartnerRead]:
    _ = admin
    statement = (
        select(Partner, City.name.label("city_name"), User.email.label("owner_email"))
        .join(City, Partner.city_id == City.id)
        .outerjoin(User, Partner.owner_user_id == User.id)
        .order_by(Partner.sort_order.asc(), Partner.id.asc())
    )

    if city_id is not None:
        statement = statement.where(Partner.city_id == city_id)
    if is_active is not None:
        statement = statement.where(Partner.is_active == is_active)
    if category_slug is not None:
        statement = statement.where(Partner.category_slug == _normalize_category_slug(category_slug))
    if q is not None:
        search = q.strip()
        if search:
            statement = statement.where(Partner.name.ilike(f"%{search}%"))

    return [
        _partner_to_read(partner, city_name, owner_email)
        for partner, city_name, owner_email in db.execute(statement).all()
    ]


@router.post("/partners", response_model=PartnerRead)
def create_admin_partner(
    payload: PartnerCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerRead:
    _ = admin
    _ensure_city_exists(db, payload.city_id)
    if payload.owner_user_id is not None:
        _get_partner_owner(db, payload.owner_user_id)

    partner = Partner(
        city_id=payload.city_id,
        owner_user_id=payload.owner_user_id,
        category_slug=_normalize_category_slug(payload.category_slug),
        name=_strip_partner_name(payload.name),
        is_active=payload.is_active,
        is_verified=payload.is_verified,
        sort_order=payload.sort_order,
    )
    for field in PARTNER_TEXT_FIELDS:
        setattr(partner, field, _normalize_optional_text(getattr(payload, field)))

    db.add(partner)
    db.commit()
    db.refresh(partner)
    return _get_partner_read_or_404(db, partner.id)


@router.get("/partners/{partner_id}", response_model=PartnerRead)
def get_admin_partner(
    partner_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerRead:
    _ = admin
    return _get_partner_read_or_404(db, partner_id)


@router.patch("/partners/{partner_id}", response_model=PartnerRead)
def update_admin_partner(
    partner_id: int,
    payload: PartnerUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerRead:
    _ = admin
    partner = db.get(Partner, partner_id)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "city_id" in update_data:
        city_id = update_data["city_id"]
        if city_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="City not found")
        _ensure_city_exists(db, city_id)
        partner.city_id = city_id
    if "owner_user_id" in update_data:
        owner_user_id = update_data["owner_user_id"]
        if owner_user_id is not None:
            _get_partner_owner(db, owner_user_id)
        partner.owner_user_id = owner_user_id
    if "category_slug" in update_data:
        partner.category_slug = _normalize_category_slug(update_data["category_slug"])
    if "name" in update_data:
        partner.name = _strip_partner_name(update_data["name"])

    for field in PARTNER_TEXT_FIELDS:
        if field in update_data:
            setattr(partner, field, _normalize_optional_text(update_data[field]))
    for field in ("is_active", "is_verified", "sort_order"):
        if field in update_data:
            setattr(partner, field, update_data[field])

    db.commit()
    db.refresh(partner)
    return _get_partner_read_or_404(db, partner.id)


@router.get("/partners/{partner_id}/offers", response_model=list[PartnerOfferRead])
def list_admin_partner_offers(
    partner_id: int,
    is_active: bool | None = None,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PartnerOfferRead]:
    _ = admin
    partner = _ensure_partner_exists(db, partner_id)
    statement = (
        select(PartnerOffer)
        .where(PartnerOffer.partner_id == partner.id)
        .order_by(PartnerOffer.sort_order.asc(), PartnerOffer.id.asc())
    )
    if is_active is not None:
        statement = statement.where(PartnerOffer.is_active == is_active)

    return [
        _partner_offer_to_read(offer, partner_name=partner.name)
        for offer in db.execute(statement).scalars().all()
    ]


@router.post("/partners/{partner_id}/offers", response_model=PartnerOfferRead)
def create_admin_partner_offer(
    partner_id: int,
    payload: PartnerOfferCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerOfferRead:
    _ = admin
    partner = _ensure_partner_exists(db, partner_id)
    _validate_offer_amounts(payload.base_price, payload.discount_percent)

    offer = PartnerOffer(
        partner_id=partner.id,
        title=_strip_offer_title(payload.title),
        base_price=payload.base_price,
        discount_percent=payload.discount_percent,
        is_active=payload.is_active,
        sort_order=payload.sort_order,
    )
    for field in PARTNER_OFFER_TEXT_FIELDS:
        setattr(offer, field, _normalize_optional_text(getattr(payload, field)))

    db.add(offer)
    db.commit()
    db.refresh(offer)
    return _partner_offer_to_read(offer, partner_name=partner.name)


@router.get("/offers/{offer_id}", response_model=PartnerOfferRead)
def get_admin_partner_offer(
    offer_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerOfferRead:
    _ = admin
    return _get_partner_offer_read_or_404(db, offer_id)


@router.patch("/offers/{offer_id}", response_model=PartnerOfferRead)
def update_admin_partner_offer(
    offer_id: int,
    payload: PartnerOfferUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerOfferRead:
    _ = admin
    offer = db.get(PartnerOffer, offer_id)
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")

    update_data = payload.model_dump(exclude_unset=True)
    _validate_offer_amounts(update_data.get("base_price"), update_data.get("discount_percent"))

    if "title" in update_data:
        offer.title = _strip_offer_title(update_data["title"])
    for field in PARTNER_OFFER_TEXT_FIELDS:
        if field in update_data:
            setattr(offer, field, _normalize_optional_text(update_data[field]))
    for field in ("base_price", "discount_percent", "is_active", "sort_order"):
        if field in update_data:
            setattr(offer, field, update_data[field])

    db.commit()
    db.refresh(offer)
    return _get_partner_offer_read_or_404(db, offer.id)


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


def _ensure_city_exists(db: Session, city_id: int) -> City:
    city = db.get(City, city_id)
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


def _get_partner_owner(db: Session, owner_user_id: int) -> User:
    owner = db.get(User, owner_user_id)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner user not found")
    if owner.role != UserRole.PARTNER.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner user must have partner role",
        )
    return owner


def _strip_partner_name(value: str | None) -> str:
    normalized = value.strip() if value is not None else ""
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner name must not be empty",
        )
    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_category_slug(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    if normalized not in WOMEN_CLUB_CATEGORY_SLUGS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown category slug")
    return normalized


def _ensure_partner_exists(db: Session, partner_id: int) -> Partner:
    partner = db.get(Partner, partner_id)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return partner


def _strip_offer_title(value: str | None) -> str:
    normalized = value.strip() if value is not None else ""
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer title must not be empty",
        )
    return normalized


def _validate_offer_amounts(
    base_price: Decimal | None = None,
    discount_percent: Decimal | None = None,
) -> None:
    if base_price is not None and base_price < Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="base_price must be greater than or equal to 0",
        )
    if discount_percent is not None and (
        discount_percent < Decimal("0") or discount_percent > Decimal("100")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="discount_percent must be between 0 and 100",
        )


def _get_partner_offer_read_or_404(db: Session, offer_id: int) -> PartnerOfferRead:
    statement = (
        select(PartnerOffer, Partner.name.label("partner_name"))
        .join(Partner, PartnerOffer.partner_id == Partner.id)
        .where(PartnerOffer.id == offer_id)
    )
    row = db.execute(statement).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    offer, partner_name = row
    return _partner_offer_to_read(offer, partner_name=partner_name)


def _partner_offer_to_read(offer: PartnerOffer, partner_name: str | None) -> PartnerOfferRead:
    return PartnerOfferRead.model_validate(
        {
            "id": offer.id,
            "partner_id": offer.partner_id,
            "title": offer.title,
            "description": offer.description,
            "benefit_text": offer.benefit_text,
            "conditions": offer.conditions,
            "base_price": offer.base_price,
            "discount_percent": offer.discount_percent,
            "image_url": offer.image_url,
            "is_active": offer.is_active,
            "sort_order": offer.sort_order,
            "partner_name": partner_name,
        }
    )


def _get_partner_read_or_404(db: Session, partner_id: int) -> PartnerRead:
    statement = (
        select(Partner, City.name.label("city_name"), User.email.label("owner_email"))
        .join(City, Partner.city_id == City.id)
        .outerjoin(User, Partner.owner_user_id == User.id)
        .where(Partner.id == partner_id)
    )
    row = db.execute(statement).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    partner, city_name, owner_email = row
    return _partner_to_read(partner, city_name, owner_email)


def _partner_to_read(partner: Partner, city_name: str | None, owner_email: str | None) -> PartnerRead:
    return PartnerRead.model_validate(
        {
            "id": partner.id,
            "city_id": partner.city_id,
            "owner_user_id": partner.owner_user_id,
            "category_slug": partner.category_slug,
            "name": partner.name,
            "description": partner.description,
            "address": partner.address,
            "phone": partner.phone,
            "website_url": partner.website_url,
            "social_url": partner.social_url,
            "working_hours": partner.working_hours,
            "logo_url": partner.logo_url,
            "cover_url": partner.cover_url,
            "is_active": partner.is_active,
            "is_verified": partner.is_verified,
            "sort_order": partner.sort_order,
            "city_name": city_name,
            "owner_email": owner_email,
        }
    )
