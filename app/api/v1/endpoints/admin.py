from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.categories import WOMEN_CLUB_CATEGORY_SLUGS
from app.core.security import hash_password
from app.db.session import get_db
from app.models.category import Category
from app.models.city import City
from app.models.client import ClientProfile
from app.models.lead import LeadClick
from app.models.partner import Partner, PartnerOffer, PartnerQrLink
from app.models.user import AdminUser, User, UserRole
from app.models.verification import PrivilegeVerificationSession
from app.schemas.admin import (
    AdminManagedUserCreate,
    AdminManagedUserRead,
    AdminManagedUserUpdate,
    AdminVerificationRead,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CityCreate,
    CityRead,
    CityUpdate,
    LeadStatsRead,
    PartnerCreate,
    PartnerOfferCreate,
    PartnerOfferRead,
    PartnerOfferUpdate,
    PartnerQrLinkCreate,
    PartnerQrLinkRead,
    PartnerQrLinkUpdate,
    PartnerRead,
    PartnerUpdate,
)
from app.schemas.auth import AdminUserRead
from app.services.image_uploads import save_partner_image_upload, validate_image_kind
from app.services.qr_links import (
    generate_qr_slug,
    is_valid_qr_slug,
    normalize_qr_slug,
    qr_link_to_read,
)

router = APIRouter(prefix="/admin", tags=["admin"])

CITY_DUPLICATE_DETAIL = "City with this slug or name already exists"
CATEGORY_DUPLICATE_DETAIL = "Category with this slug already exists"
USER_DUPLICATE_DETAIL = "User with this email or phone already exists"
ALLOWED_USER_ROLES = tuple(role.value for role in UserRole)
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


@router.get("/verifications", response_model=list[AdminVerificationRead])
def list_admin_verifications(
    partner_id: int | None = None,
    client_id: int | None = None,
    status: str | None = None,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminVerificationRead]:
    _ = admin
    statement = (
        select(
            PrivilegeVerificationSession,
            ClientProfile.full_name.label("client_name"),
            Partner.name.label("partner_name"),
            City.id.label("city_id"),
            City.name.label("city_name"),
            PartnerOffer.title.label("offer_title"),
        )
        .join(ClientProfile, PrivilegeVerificationSession.client_id == ClientProfile.id)
        .join(Partner, PrivilegeVerificationSession.partner_id == Partner.id)
        .join(City, Partner.city_id == City.id)
        .outerjoin(PartnerOffer, PrivilegeVerificationSession.offer_id == PartnerOffer.id)
        .order_by(PrivilegeVerificationSession.created_at.desc(), PrivilegeVerificationSession.id.desc())
    )
    if partner_id is not None:
        statement = statement.where(PrivilegeVerificationSession.partner_id == partner_id)
    if client_id is not None:
        statement = statement.where(PrivilegeVerificationSession.client_id == client_id)
    if status is not None:
        statement = statement.where(PrivilegeVerificationSession.status == status)

    return [
        _admin_verification_to_read(session, client_name, partner_name, city_id, city_name, offer_title)
        for session, client_name, partner_name, city_id, city_name, offer_title in db.execute(statement).all()
    ]


@router.get("/users", response_model=list[AdminManagedUserRead])
def list_admin_users(
    role: str | None = None,
    is_active: bool | None = None,
    q: str | None = None,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    _ = admin
    statement = select(User).order_by(User.id.asc())

    if role is not None:
        statement = statement.where(User.role == _normalize_user_role(role))
    if is_active is not None:
        statement = statement.where(User.is_active == is_active)
    if q is not None:
        search = q.strip()
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(User.email.ilike(pattern), User.phone.ilike(pattern)))

    return list(db.execute(statement).scalars().all())


@router.post("/users", response_model=AdminManagedUserRead)
def create_admin_user(
    payload: AdminManagedUserCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    _ = admin
    email = _normalize_user_email(payload.email)
    phone = _normalize_user_phone(payload.phone)
    _ensure_user_contact_present(email, phone)
    role = _normalize_user_role(payload.role)
    password = _normalize_user_password(payload.password)
    _ensure_unique_user_identity(db, email=email, phone=phone)

    user = User(
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role=role,
        is_active=payload.is_active,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _user_duplicate_error() from None
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=AdminManagedUserRead)
def update_admin_user(
    user_id: int,
    payload: AdminManagedUserUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    _ = admin
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    next_email = _normalize_user_email(update_data["email"]) if "email" in update_data else user.email
    next_phone = _normalize_user_phone(update_data["phone"]) if "phone" in update_data else user.phone
    _ensure_user_contact_present(next_email, next_phone)
    _ensure_unique_user_identity(db, email=next_email, phone=next_phone, exclude_user_id=user.id)

    if "email" in update_data:
        user.email = next_email
    if "phone" in update_data:
        user.phone = next_phone
    if "role" in update_data:
        user.role = _normalize_user_role(update_data["role"])
    if "is_active" in update_data:
        user.is_active = update_data["is_active"]
    if "password" in update_data:
        if update_data["password"] is not None:
            user.password_hash = hash_password(_normalize_user_password(update_data["password"]))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _user_duplicate_error() from None
    db.refresh(user)
    return user


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
def list_admin_categories(
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[Category]:
    _ = admin
    result = db.execute(select(Category).order_by(Category.sort_order.asc(), Category.id.asc()))
    return list(result.scalars().all())


@router.post("/categories", response_model=CategoryRead)
def create_admin_category(
    payload: CategoryCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Category:
    _ = admin
    name = _strip_category_required(payload.name, "name")
    slug = _strip_category_required(payload.slug, "slug")
    _ensure_unique_category_slug(db, slug=slug)

    category = Category(
        name=name,
        slug=slug,
        is_active=payload.is_active,
        sort_order=payload.sort_order if payload.sort_order is not None else 0,
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _category_duplicate_error() from None
    db.refresh(category)
    return category


@router.patch("/categories/{category_id}", response_model=CategoryRead)
def update_admin_category(
    category_id: int,
    payload: CategoryUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Category:
    _ = admin
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    update_data = payload.model_dump(exclude_unset=True)
    next_slug = _strip_category_required(update_data["slug"], "slug") if "slug" in update_data else category.slug
    if next_slug != category.slug:
        _ensure_unique_category_slug(db, slug=next_slug, exclude_category_id=category.id)

    for field, value in update_data.items():
        if field == "name":
            category.name = _strip_category_required(value, "name")
        elif field == "slug":
            category.slug = next_slug
        elif field == "is_active":
            category.is_active = value
        elif field == "sort_order":
            category.sort_order = value if value is not None else 0

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _category_duplicate_error() from None
    db.refresh(category)
    return category


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
        statement = statement.where(Partner.category_slug == _normalize_category_slug(db, category_slug))
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
        category_slug=_normalize_category_slug(db, payload.category_slug),
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
        partner.category_slug = _normalize_category_slug(db, update_data["category_slug"])
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


@router.post("/partners/{partner_id}/images")
async def upload_admin_partner_image(
    partner_id: int,
    kind: str,
    file: UploadFile = File(...),
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    _ = admin
    partner = _ensure_partner_exists(db, partner_id)
    normalized_kind = validate_image_kind(kind)
    image_url = await save_partner_image_upload(partner.id, normalized_kind, file)
    setattr(partner, f"{normalized_kind}_url", image_url)
    db.commit()
    return {"url": image_url, "kind": normalized_kind}


@router.post("/partners/{partner_id}/qr-links", response_model=PartnerQrLinkRead)
def create_admin_partner_qr_link(
    partner_id: int,
    payload: PartnerQrLinkCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerQrLinkRead:
    _ = admin
    partner = _ensure_partner_exists(db, partner_id)
    slug = _normalize_or_generate_qr_slug(db, partner.id, payload.slug)

    qr_link = PartnerQrLink(
        partner_id=partner.id,
        slug=slug,
        deep_link_payload=_normalize_optional_text(payload.deep_link_payload),
        target_url=_normalize_optional_text(payload.target_url),
        is_active=payload.is_active,
    )
    db.add(qr_link)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _qr_slug_duplicate_error() from None
    db.refresh(qr_link)
    return PartnerQrLinkRead.model_validate(qr_link_to_read(qr_link, partner_name=partner.name))


@router.get("/partners/{partner_id}/qr-links", response_model=list[PartnerQrLinkRead])
def list_admin_partner_qr_links(
    partner_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PartnerQrLinkRead]:
    _ = admin
    partner = _ensure_partner_exists(db, partner_id)
    links = db.execute(
        select(PartnerQrLink)
        .where(PartnerQrLink.partner_id == partner.id)
        .order_by(PartnerQrLink.id.asc())
    ).scalars().all()
    return [
        PartnerQrLinkRead.model_validate(qr_link_to_read(link, partner_name=partner.name))
        for link in links
    ]


@router.patch("/qr-links/{qr_link_id}", response_model=PartnerQrLinkRead)
def update_admin_qr_link(
    qr_link_id: int,
    payload: PartnerQrLinkUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PartnerQrLinkRead:
    _ = admin
    row = db.execute(
        select(PartnerQrLink, Partner.name.label("partner_name"))
        .join(Partner, PartnerQrLink.partner_id == Partner.id)
        .where(PartnerQrLink.id == qr_link_id)
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR link not found")
    qr_link, partner_name = row

    update_data = payload.model_dump(exclude_unset=True)
    if "slug" in update_data:
        qr_link.slug = _normalize_existing_qr_slug(db, update_data["slug"], exclude_qr_link_id=qr_link.id)
    if "deep_link_payload" in update_data:
        qr_link.deep_link_payload = _normalize_optional_text(update_data["deep_link_payload"])
    if "target_url" in update_data:
        qr_link.target_url = _normalize_optional_text(update_data["target_url"])
    if "is_active" in update_data:
        qr_link.is_active = update_data["is_active"]

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _qr_slug_duplicate_error() from None
    db.refresh(qr_link)
    return PartnerQrLinkRead.model_validate(qr_link_to_read(qr_link, partner_name=partner_name))


@router.get("/leads/partners", response_model=list[LeadStatsRead])
def list_admin_partner_lead_stats(
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[LeadStatsRead]:
    _ = admin
    rows = db.execute(
        select(
            Partner.id.label("partner_id"),
            Partner.name.label("partner_name"),
            City.id.label("city_id"),
            City.name.label("city_name"),
            PartnerQrLink.id.label("qr_link_id"),
            PartnerQrLink.slug.label("qr_slug"),
            func.count(LeadClick.id).label("total_clicks"),
        )
        .join(Partner, LeadClick.partner_id == Partner.id)
        .outerjoin(City, LeadClick.city_id == City.id)
        .outerjoin(PartnerQrLink, LeadClick.qr_link_id == PartnerQrLink.id)
        .group_by(Partner.id, Partner.name, City.id, City.name, PartnerQrLink.id, PartnerQrLink.slug)
        .order_by(func.count(LeadClick.id).desc(), Partner.id.asc())
    ).all()
    return [LeadStatsRead.model_validate(dict(row._mapping)) for row in rows]


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


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _ttl_seconds(expires_at: datetime) -> int | None:
    seconds = int((_as_aware_utc(expires_at) - datetime.now(timezone.utc)).total_seconds())
    return max(seconds, 0)


def _admin_verification_to_read(
    session: PrivilegeVerificationSession,
    client_name: str | None,
    partner_name: str | None,
    city_id: int | None,
    city_name: str | None,
    offer_title: str | None,
) -> AdminVerificationRead:
    return AdminVerificationRead.model_validate(
        {
            "id": session.id,
            "client_id": session.client_id,
            "client_name": client_name,
            "partner_id": session.partner_id,
            "partner_name": partner_name,
            "city_id": city_id,
            "city_name": city_name,
            "offer_id": session.offer_id,
            "offer_title": offer_title,
            "code": session.code,
            "status": session.status,
            "source": session.source,
            "expires_at": session.expires_at,
            "confirmed_at": session.confirmed_at,
            "created_at": session.created_at,
            "ttl_seconds": _ttl_seconds(session.expires_at),
        }
    )


def _normalize_user_email(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _normalize_user_phone(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _ensure_user_contact_present(email: str | None, phone: str | None) -> None:
    if email is None and phone is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is required",
        )


def _normalize_user_role(value: str | None) -> str:
    normalized = value.strip().lower() if value is not None else ""
    if normalized not in ALLOWED_USER_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user role")
    return normalized


def _normalize_user_password(value: str) -> str:
    normalized = value.strip()
    if len(normalized) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )
    return normalized


def _ensure_unique_user_identity(
    db: Session,
    *,
    email: str | None,
    phone: str | None,
    exclude_user_id: int | None = None,
) -> None:
    conditions = []
    if email is not None:
        conditions.append(User.email == email)
    if phone is not None:
        conditions.append(User.phone == phone)
    if not conditions:
        return

    statement = select(User.id).where(or_(*conditions))
    if exclude_user_id is not None:
        statement = statement.where(User.id != exclude_user_id)
    duplicate_id = db.execute(statement.limit(1)).scalar_one_or_none()
    if duplicate_id is not None:
        raise _user_duplicate_error()


def _user_duplicate_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_DUPLICATE_DETAIL)


def _qr_slug_duplicate_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="QR slug already exists")


def _invalid_qr_slug_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid QR slug")


def _ensure_unique_qr_slug(db: Session, slug: str, exclude_qr_link_id: int | None = None) -> None:
    statement = select(PartnerQrLink.id).where(PartnerQrLink.slug == slug)
    if exclude_qr_link_id is not None:
        statement = statement.where(PartnerQrLink.id != exclude_qr_link_id)
    duplicate_id = db.execute(statement.limit(1)).scalar_one_or_none()
    if duplicate_id is not None:
        raise _qr_slug_duplicate_error()


def _normalize_existing_qr_slug(
    db: Session,
    slug: str | None,
    *,
    exclude_qr_link_id: int | None = None,
) -> str:
    normalized = normalize_qr_slug(slug)
    if not is_valid_qr_slug(normalized):
        raise _invalid_qr_slug_error()
    assert normalized is not None
    _ensure_unique_qr_slug(db, normalized, exclude_qr_link_id=exclude_qr_link_id)
    return normalized


def _normalize_or_generate_qr_slug(db: Session, partner_id: int, slug: str | None) -> str:
    if slug is not None:
        return _normalize_existing_qr_slug(db, slug)
    for _ in range(5):
        generated = generate_qr_slug(partner_id)
        if is_valid_qr_slug(generated):
            existing_id = db.execute(
                select(PartnerQrLink.id).where(PartnerQrLink.slug == generated).limit(1)
            ).scalar_one_or_none()
            if existing_id is None:
                return generated
    raise _qr_slug_duplicate_error()


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


def _strip_category_required(value: str | None, field_name: str) -> str:
    normalized = value.strip() if value is not None else ""
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category {field_name} must not be empty",
        )
    return normalized


def _ensure_unique_category_slug(
    db: Session,
    *,
    slug: str,
    exclude_category_id: int | None = None,
) -> None:
    statement = select(Category.id).where(Category.slug == slug)
    if exclude_category_id is not None:
        statement = statement.where(Category.id != exclude_category_id)
    duplicate_id = db.execute(statement.limit(1)).scalar_one_or_none()
    if duplicate_id is not None:
        raise _category_duplicate_error()


def _category_duplicate_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=CATEGORY_DUPLICATE_DETAIL)


def _normalize_category_slug(db: Session, value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    category_count = db.execute(select(func.count()).select_from(Category)).scalar_one()
    if category_count == 0:
        if normalized not in WOMEN_CLUB_CATEGORY_SLUGS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown category slug")
        return normalized

    category_id = db.execute(
        select(Category.id).where(Category.slug == normalized, Category.is_active.is_(True)).limit(1)
    ).scalar_one_or_none()
    if category_id is None:
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
