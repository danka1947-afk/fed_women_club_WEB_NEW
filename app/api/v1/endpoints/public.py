from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.session import get_db
from app.models.lead import LeadClick
from app.models.partner import PartnerQrLink

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
