from __future__ import annotations

import hashlib

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.session import get_db
from app.models.category import Category
from app.models.city import City
from app.models.lead import LeadClick
from app.models.partner import Partner, PartnerOffer, PartnerQrLink
from app.schemas.partner import (
    PublicLandingPartnerCard,
    PublicLandingPartnerListResponse,
    PublicLandingPartnerOffer,
)

router = APIRouter(tags=["public"])


def _hash_visitor_value(value: str | None) -> str | None:
    if not value:
        return None
    salt = settings.JWT_SECRET_KEY or "womenclub"
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()


def _normalize_optional_query_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_slug_query_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _format_discount_percent(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return f"-{normalized}%"


def _public_landing_offer_to_read(offer: PartnerOffer) -> PublicLandingPartnerOffer:
    return PublicLandingPartnerOffer(
        title=offer.title,
        discount_text=offer.benefit_text or _format_discount_percent(offer.discount_percent),
        description=offer.description,
        terms=offer.conditions,
    )


def _public_landing_partner_to_read(
    partner: Partner,
    city: City,
    category: Category,
    offers: list[PartnerOffer],
) -> PublicLandingPartnerCard:
    return PublicLandingPartnerCard(
        id=partner.id,
        name=partner.name,
        address=partner.address,
        city_name=city.name,
        city_slug=city.slug,
        category_title=category.title,
        category_slug=category.slug,
        logo_url=partner.logo_url,
        cover_url=partner.cover_url,
        offers=[_public_landing_offer_to_read(offer) for offer in offers],
    )


@router.get("/r/p/{slug}")
def redirect_partner_qr_link(
    slug: str,
    request: Request,
    session_id: str | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    qr_link = db.execute(
        select(PartnerQrLink)
        .options(joinedload(PartnerQrLink.partner))
        .where(PartnerQrLink.slug == slug, PartnerQrLink.is_active.is_(True))
    ).scalar_one_or_none()
    if qr_link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR link not found")

    client_host = request.client.host if request.client is not None else None
    lead_click = LeadClick(
        partner_id=qr_link.partner_id,
        qr_link_id=qr_link.id,
        city_id=qr_link.partner.city_id if qr_link.partner is not None else None,
        source="web_qr",
        session_id=_normalize_optional_query_value(session_id),
        ip_hash=_hash_visitor_value(client_host),
        user_agent_hash=_hash_visitor_value(request.headers.get("user-agent")),
        referer=_normalize_optional_query_value(request.headers.get("referer")),
        utm_source=_normalize_optional_query_value(utm_source),
        utm_medium=_normalize_optional_query_value(utm_medium),
        utm_campaign=_normalize_optional_query_value(utm_campaign),
    )
    db.add(lead_click)
    db.commit()

    target_url = qr_link.target_url or qr_link.deep_link_payload or f"{settings.WEB_PUBLIC_URL.rstrip('/')}/"
    return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)


@router.get("/api/v1/public/landing/partners", response_model=PublicLandingPartnerListResponse)
def list_public_landing_partners(
    category_slug: str | None = None,
    city_slug: str | None = None,
    limit: int = Query(default=12, ge=1),
    db: Session = Depends(get_db),
) -> PublicLandingPartnerListResponse:
    normalized_category_slug = _normalize_slug_query_value(category_slug)
    normalized_city_slug = _normalize_slug_query_value(city_slug)
    safe_limit = min(limit, 30)

    if category_slug is not None:
        category_exists = db.execute(
            select(Category.id).where(
                Category.slug == normalized_category_slug,
                Category.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if category_exists is None:
            return PublicLandingPartnerListResponse(items=[])

    if city_slug is not None:
        city_exists = db.execute(
            select(City.id).where(
                City.slug == normalized_city_slug,
                City.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if city_exists is None:
            return PublicLandingPartnerListResponse(items=[])

    statement = (
        select(Partner, City, Category)
        .join(City, Partner.city_id == City.id)
        .join(Category, Partner.category_slug == Category.slug)
        .where(
            Partner.is_active.is_(True),
            Partner.is_verified.is_(True),
            City.is_active.is_(True),
            Category.is_active.is_(True),
        )
        .order_by(Partner.sort_order.asc(), Partner.id.asc())
        .limit(safe_limit)
    )

    if normalized_category_slug is not None:
        statement = statement.where(Category.slug == normalized_category_slug)
    if normalized_city_slug is not None:
        statement = statement.where(City.slug == normalized_city_slug)

    rows = db.execute(statement).all()
    partner_ids = [partner.id for partner, _city, _category in rows]
    offers_by_partner: dict[int, list[PartnerOffer]] = {partner_id: [] for partner_id in partner_ids}
    if partner_ids:
        offers = db.execute(
            select(PartnerOffer)
            .where(
                PartnerOffer.partner_id.in_(partner_ids),
                PartnerOffer.is_active.is_(True),
            )
            .order_by(PartnerOffer.sort_order.asc(), PartnerOffer.id.asc())
        ).scalars().all()
        for offer in offers:
            offers_by_partner.setdefault(offer.partner_id, []).append(offer)

    return PublicLandingPartnerListResponse(
        items=[
            _public_landing_partner_to_read(partner, city, category, offers_by_partner.get(partner.id, []))
            for partner, city, category in rows
        ]
    )
