from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_partner
from app.db.session import get_db
from app.models.city import City
from app.models.client import ClientProfile
from app.models.lead import LeadClick
from app.models.partner import Partner, PartnerOffer, PartnerQrLink
from app.models.verification import PrivilegeVerificationSession, PrivilegeVerificationStatus
from app.models.user import User
from app.schemas.partner import (
    ConfirmVerificationResponse,
    PartnerOfferCreate,
    PartnerOfferRead,
    LeadStatsRead,
    PartnerOfferUpdate,
    PartnerQrLinkRead,
    PartnerProfileRead,
    PartnerProfileUpdate,
    PartnerVerificationRead,
)
from app.services.qr_links import qr_link_to_read

router = APIRouter(prefix="/partners", tags=["partners"])

PARTNER_PROFILE_TEXT_FIELDS = (
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
PARTNER_NOT_FOUND_DETAIL = "Partner profile for current user was not found"
VERIFICATION_NOT_FOUND_DETAIL = "Verification session not found"


@router.get("/me", response_model=PartnerProfileRead)
def read_partner_me(
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> PartnerProfileRead:
    partner = _get_current_partner_or_404(db, current_user.id)
    return _get_partner_profile_read(db, partner.id)


@router.patch("/me", response_model=PartnerProfileRead)
def update_partner_me(
    payload: PartnerProfileUpdate,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> PartnerProfileRead:
    partner = _get_current_partner_or_404(db, current_user.id)
    update_data = payload.model_dump(exclude_unset=True)

    for field in PARTNER_PROFILE_TEXT_FIELDS:
        if field in update_data:
            setattr(partner, field, _normalize_optional_text(update_data[field]))

    db.commit()
    db.refresh(partner)
    return _get_partner_profile_read(db, partner.id)


@router.get("/me/qr-links", response_model=list[PartnerQrLinkRead])
def list_partner_qr_links(
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> list[PartnerQrLinkRead]:
    partner = _get_current_partner_or_404(db, current_user.id)
    links = db.execute(
        select(PartnerQrLink)
        .where(PartnerQrLink.partner_id == partner.id)
        .order_by(PartnerQrLink.id.asc())
    ).scalars().all()
    return [
        PartnerQrLinkRead.model_validate(qr_link_to_read(link, partner_name=partner.name))
        for link in links
    ]


@router.get("/me/leads", response_model=list[LeadStatsRead])
def list_partner_lead_stats(
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> list[LeadStatsRead]:
    partner = _get_current_partner_or_404(db, current_user.id)
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
        .where(LeadClick.partner_id == partner.id)
        .group_by(Partner.id, Partner.name, City.id, City.name, PartnerQrLink.id, PartnerQrLink.slug)
        .order_by(func.count(LeadClick.id).desc(), PartnerQrLink.id.asc())
    ).all()
    return [LeadStatsRead.model_validate(dict(row._mapping)) for row in rows]


@router.get("/me/verifications", response_model=list[PartnerVerificationRead])
def list_partner_verifications(
    status: str | None = None,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> list[PartnerVerificationRead]:
    partner = _get_current_partner_or_404(db, current_user.id)
    statement = (
        select(
            PrivilegeVerificationSession,
            ClientProfile.full_name.label("client_name"),
            Partner.name.label("partner_name"),
            PartnerOffer.title.label("offer_title"),
        )
        .join(ClientProfile, PrivilegeVerificationSession.client_id == ClientProfile.id)
        .join(Partner, PrivilegeVerificationSession.partner_id == Partner.id)
        .outerjoin(PartnerOffer, PrivilegeVerificationSession.offer_id == PartnerOffer.id)
        .where(PrivilegeVerificationSession.partner_id == partner.id)
        .order_by(PrivilegeVerificationSession.created_at.desc(), PrivilegeVerificationSession.id.desc())
    )
    if status is not None:
        statement = statement.where(PrivilegeVerificationSession.status == status)

    return [
        _partner_verification_to_read(session, client_name, partner_name, offer_title)
        for session, client_name, partner_name, offer_title in db.execute(statement).all()
    ]


@router.post("/me/verifications/{verification_id}/confirm", response_model=ConfirmVerificationResponse)
def confirm_partner_verification(
    verification_id: int,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> ConfirmVerificationResponse:
    partner = _get_current_partner_or_404(db, current_user.id)
    verification = db.execute(
        select(PrivilegeVerificationSession).where(
            PrivilegeVerificationSession.id == verification_id,
            PrivilegeVerificationSession.partner_id == partner.id,
        )
    ).scalar_one_or_none()
    if verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VERIFICATION_NOT_FOUND_DETAIL)

    if verification.status != PrivilegeVerificationStatus.active.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification session is not active")

    now = datetime.now(timezone.utc)
    if _as_aware_utc(verification.expires_at) < now:
        verification.status = PrivilegeVerificationStatus.expired.value
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification session expired")

    verification.status = PrivilegeVerificationStatus.confirmed.value
    verification.confirmed_at = now
    db.commit()
    db.refresh(verification)
    return ConfirmVerificationResponse.model_validate(
        {
            "id": verification.id,
            "status": verification.status,
            "confirmed_at": verification.confirmed_at,
        }
    )


@router.get("/me/offers", response_model=list[PartnerOfferRead])
def list_partner_offers(
    is_active: bool | None = None,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> list[PartnerOfferRead]:
    partner = _get_current_partner_or_404(db, current_user.id)
    statement = (
        select(PartnerOffer)
        .where(PartnerOffer.partner_id == partner.id)
        .order_by(PartnerOffer.sort_order.asc(), PartnerOffer.id.asc())
    )
    if is_active is not None:
        statement = statement.where(PartnerOffer.is_active == is_active)

    return [_partner_offer_to_read(offer) for offer in db.execute(statement).scalars().all()]


@router.post("/me/offers", response_model=PartnerOfferRead)
def create_partner_offer(
    payload: PartnerOfferCreate,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> PartnerOfferRead:
    partner = _get_current_partner_or_404(db, current_user.id)
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
    return _partner_offer_to_read(offer)


@router.patch("/me/offers/{offer_id}", response_model=PartnerOfferRead)
def update_partner_offer(
    offer_id: int,
    payload: PartnerOfferUpdate,
    current_user: User = Depends(require_partner),
    db: Session = Depends(get_db),
) -> PartnerOfferRead:
    partner = _get_current_partner_or_404(db, current_user.id)
    offer = _get_owned_offer_or_404(db, partner.id, offer_id)
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
    return _partner_offer_to_read(offer)


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _ttl_seconds(expires_at: datetime) -> int | None:
    seconds = int((_as_aware_utc(expires_at) - datetime.now(timezone.utc)).total_seconds())
    return max(seconds, 0)


def _partner_verification_to_read(
    session: PrivilegeVerificationSession,
    client_name: str | None,
    partner_name: str | None,
    offer_title: str | None,
) -> PartnerVerificationRead:
    return PartnerVerificationRead.model_validate(
        {
            "id": session.id,
            "client_id": session.client_id,
            "client_name": client_name,
            "partner_id": session.partner_id,
            "partner_name": partner_name,
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


def _get_current_partner_or_404(db: Session, owner_user_id: int) -> Partner:
    partner = db.execute(select(Partner).where(Partner.owner_user_id == owner_user_id)).scalars().first()
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PARTNER_NOT_FOUND_DETAIL)
    return partner


def _get_partner_profile_read(db: Session, partner_id: int) -> PartnerProfileRead:
    row = db.execute(
        select(Partner, City.name.label("city_name"))
        .join(City, Partner.city_id == City.id)
        .where(Partner.id == partner_id)
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PARTNER_NOT_FOUND_DETAIL)
    partner, city_name = row
    return PartnerProfileRead.model_validate(
        {
            "id": partner.id,
            "city_id": partner.city_id,
            "city_name": city_name,
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
        }
    )


def _get_owned_offer_or_404(db: Session, partner_id: int, offer_id: int) -> PartnerOffer:
    offer = db.execute(
        select(PartnerOffer).where(
            PartnerOffer.id == offer_id,
            PartnerOffer.partner_id == partner_id,
        )
    ).scalar_one_or_none()
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    return offer


def _strip_offer_title(value: str | None) -> str:
    normalized = value.strip() if value is not None else ""
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer title must not be empty",
        )
    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


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


def _partner_offer_to_read(offer: PartnerOffer) -> PartnerOfferRead:
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
        }
    )
