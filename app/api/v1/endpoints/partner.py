from __future__ import annotations

from datetime import datetime, time, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.client import ClientProfile
from app.models.partner import Partner, PartnerOffer
from app.models.payment import Subscription, SubscriptionStatus
from app.models.user import User, UserRole
from app.models.verification import PrivilegeVerificationSession, PrivilegeVerificationStatus
from app.schemas.partner import (
    PartnerMePartnerRead,
    PartnerMeResponse,
    PartnerPrivilegeClientRead,
    PartnerPrivilegeConfirmRequest,
    PartnerPrivilegeConfirmResponse,
    PartnerPrivilegePartnerRead,
    PartnerPrivilegeRead,
    PartnerPrivilegeScanRequest,
    PartnerPrivilegeScanResponse,
    PartnerStats,
)
from app.services.privilege_verifications import as_aware_utc, normalize_expired_verifications

router = APIRouter(prefix="/partner", tags=["partner"])

PRIVILEGE_QR_PAYLOAD_PREFIX = "bloomclub:privilege:"
PARTNER_ACCESS_REQUIRED_DETAIL = "Partner access required"
QR_NOT_FOUND_DETAIL = "QR not found"
QR_EXPIRED_DETAIL = "QR expired"
QR_ALREADY_CONFIRMED_DETAIL = "QR already confirmed"
QR_ANOTHER_PARTNER_DETAIL = "QR belongs to another partner"
ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL = "Active subscription required"
QR_NOT_CONFIRMABLE_DETAIL = "QR is not confirmable"
CONFIRMABLE_STATUSES = {
    PrivilegeVerificationStatus.pending.value,
    PrivilegeVerificationStatus.active.value,
}


@router.get("/me", response_model=PartnerMeResponse)
def read_partner_dashboard_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PartnerMeResponse:
    partner = _get_current_partner(db, current_user)
    if partner is None:
        return PartnerMeResponse(is_partner=False, partner=None, stats=None)
    return PartnerMeResponse(
        is_partner=True,
        partner=_partner_me_read(partner),
        stats=_partner_stats(db, partner.id),
    )


@router.post("/privileges/scan", response_model=PartnerPrivilegeScanResponse)
def scan_partner_privilege(
    payload: PartnerPrivilegeScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PartnerPrivilegeScanResponse:
    partner = _require_current_partner(db, current_user)
    now = datetime.now(timezone.utc)
    normalize_expired_verifications(db, now=now)
    session = _find_session_for_scan(db, payload)
    _validate_session_for_partner_action(db, session, partner.id, now=now)
    return _scan_response(db, session, partner, now)


@router.post("/privileges/confirm", response_model=PartnerPrivilegeConfirmResponse)
def confirm_partner_privilege(
    payload: PartnerPrivilegeConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PartnerPrivilegeConfirmResponse:
    partner = _require_current_partner(db, current_user)
    now = datetime.now(timezone.utc)
    normalize_expired_verifications(db, now=now)
    session = db.execute(
        select(PrivilegeVerificationSession)
        .options(
            selectinload(PrivilegeVerificationSession.client),
            selectinload(PrivilegeVerificationSession.partner),
            selectinload(PrivilegeVerificationSession.offer),
        )
        .where(PrivilegeVerificationSession.id == payload.session_id)
    ).scalar_one_or_none()
    _validate_session_for_partner_action(db, session, partner.id, now=now)

    session.status = PrivilegeVerificationStatus.confirmed.value
    session.confirmed_at = now
    session.confirmed_by_partner_id = partner.id
    if payload.saving_amount is not None:
        session.saving_amount = payload.saving_amount
    elif session.saving_amount is None:
        session.saving_amount = Decimal("0.00")
    session.saving_partner_name = session.partner.name if session.partner is not None else partner.name
    session.saving_offer_title = session.offer.title if session.offer is not None else None
    session.saving_used_at = now
    db.commit()
    db.refresh(session)
    return PartnerPrivilegeConfirmResponse(
        status=session.status,
        confirmed_at=session.confirmed_at,
        saving_amount=session.saving_amount,
    )


def _get_current_partner(db: Session, current_user: User) -> Partner | None:
    if current_user.role != UserRole.PARTNER.value:
        return None
    return db.execute(
        select(Partner).where(
            Partner.owner_user_id == current_user.id,
            Partner.is_active.is_(True),
        )
    ).scalars().first()


def _require_current_partner(db: Session, current_user: User) -> Partner:
    partner = _get_current_partner(db, current_user)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=PARTNER_ACCESS_REQUIRED_DETAIL)
    return partner


def _partner_me_read(partner: Partner) -> PartnerMePartnerRead:
    return PartnerMePartnerRead(
        id=partner.id,
        name=partner.name,
        display_name=partner.name,
        is_active=partner.is_active,
    )


def _partner_stats(db: Session, partner_id: int) -> PartnerStats:
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    confirmed_filters = (
        PrivilegeVerificationSession.partner_id == partner_id,
        PrivilegeVerificationSession.status == PrivilegeVerificationStatus.confirmed.value,
        PrivilegeVerificationSession.confirmed_at.is_not(None),
    )
    confirmed_today = db.execute(
        select(func.count(PrivilegeVerificationSession.id)).where(
            *confirmed_filters,
            PrivilegeVerificationSession.confirmed_at >= today_start,
        )
    ).scalar_one()
    row = db.execute(
        select(
            func.count(PrivilegeVerificationSession.id),
            func.coalesce(func.sum(PrivilegeVerificationSession.saving_amount), 0),
        ).where(
            *confirmed_filters,
            PrivilegeVerificationSession.confirmed_at >= month_start,
        )
    ).one()
    return PartnerStats(
        confirmed_today=int(confirmed_today or 0),
        confirmed_month=int(row[0] or 0),
        savings_month=row[1] or Decimal("0.00"),
    )


def _find_session_for_scan(db: Session, payload: PartnerPrivilegeScanRequest) -> PrivilegeVerificationSession | None:
    token = _extract_token(payload.qr_payload)
    statement = (
        select(PrivilegeVerificationSession)
        .options(
            selectinload(PrivilegeVerificationSession.client),
            selectinload(PrivilegeVerificationSession.partner),
            selectinload(PrivilegeVerificationSession.offer),
        )
    )
    if token is not None:
        return db.execute(statement.where(PrivilegeVerificationSession.token == token)).scalar_one_or_none()
    code = (payload.code or "").strip()
    if code:
        return db.execute(statement.where(PrivilegeVerificationSession.code == code)).scalar_one_or_none()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=QR_NOT_FOUND_DETAIL)


def _extract_token(qr_payload: str | None) -> str | None:
    value = (qr_payload or "").strip()
    if not value:
        return None
    if not value.startswith(PRIVILEGE_QR_PAYLOAD_PREFIX):
        return None
    token = value.removeprefix(PRIVILEGE_QR_PAYLOAD_PREFIX).strip()
    return token or None


def _validate_session_for_partner_action(
    db: Session,
    session: PrivilegeVerificationSession | None,
    partner_id: int,
    *,
    now: datetime,
) -> None:
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=QR_NOT_FOUND_DETAIL)
    if session.partner_id != partner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=QR_ANOTHER_PARTNER_DETAIL)
    if session.status == PrivilegeVerificationStatus.confirmed.value or session.confirmed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=QR_ALREADY_CONFIRMED_DETAIL)
    if session.status == PrivilegeVerificationStatus.expired.value or as_aware_utc(session.expires_at) < now:
        session.status = PrivilegeVerificationStatus.expired.value
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=QR_EXPIRED_DETAIL)
    if session.status not in CONFIRMABLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=QR_NOT_CONFIRMABLE_DETAIL)
    if not _has_active_subscription(db, session.client_id, now):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL)


def _has_active_subscription(db: Session, client_id: int, now: datetime) -> bool:
    return db.execute(
        select(Subscription.id)
        .where(
            Subscription.client_id == client_id,
            Subscription.status == SubscriptionStatus.active.value,
            Subscription.starts_at <= now,
            Subscription.ends_at > now,
        )
        .limit(1)
    ).scalar_one_or_none() is not None


def _scan_response(
    db: Session,
    session: PrivilegeVerificationSession,
    partner: Partner,
    now: datetime,
) -> PartnerPrivilegeScanResponse:
    client = session.client or db.get(ClientProfile, session.client_id)
    privilege = session.offer or (db.get(PartnerOffer, session.offer_id) if session.offer_id is not None else None)
    return PartnerPrivilegeScanResponse(
        session_id=session.id,
        status=session.status,
        can_confirm=True,
        client=PartnerPrivilegeClientRead(
            display_name=(client.full_name if client is not None else None) or "Client",
            subscription_active=_has_active_subscription(db, session.client_id, now),
        ),
        partner=PartnerPrivilegePartnerRead(id=partner.id, name=partner.name),
        privilege=(
            PartnerPrivilegeRead(id=privilege.id, title=privilege.title)
            if privilege is not None
            else None
        ),
        expires_at=session.expires_at,
    )
