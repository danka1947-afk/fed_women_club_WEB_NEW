from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_client
from app.db.session import get_db
from app.models.city import City
from app.models.client import ClientProfile, VkLinkCode, VkLinkCodeStatus
from app.models.partner import Partner, PartnerOffer, PartnerPhoto
from app.models.payment import PaymentReceipt, PaymentRequest, PaymentRequestStatus, Subscription, SubscriptionStatus
from app.models.verification import PrivilegeVerificationSession, PrivilegeVerificationStatus
from app.models.user import User
from app.schemas.activity import ActivityFeedRead
from app.schemas.client import (
    ClientCreateVerificationRequest,
    ClientPartnerCatalogItem,
    ClientPartnerOfferRead,
    ClientPartnerPhotoRead,
    ClientProfileRead,
    ClientProfileUpdate,
    ClientVerificationRead,
    SubscriptionRead,
)
from app.schemas.payment import (
    PaymentReceiptCreate,
    PaymentReceiptRead,
    PaymentRequestCreate,
    PaymentRequestMarkPaid,
    PaymentRequestRead,
)
from app.schemas.vk import VkLinkCodeRead
from app.services.activity_feed import build_client_activity_feed

router = APIRouter(prefix="/clients", tags=["clients"])

CITY_NOT_FOUND_DETAIL = "City not found"
PARTNER_NOT_FOUND_DETAIL = "Partner not found"
OFFER_NOT_FOUND_DETAIL = "Offer not found"
ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL = "Active subscription required"
VERIFICATION_TTL_SECONDS = 5 * 60
VERIFICATION_CODE_ALPHABET = string.digits
VK_LINK_CODE_TTL_SECONDS = 10 * 60
VK_LINK_CODE_LENGTH = 8
VK_LINK_CODE_ALPHABET = string.ascii_uppercase + string.digits


@router.get("/me", response_model=ClientProfileRead)
def read_client_me(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientProfileRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    return _client_profile_to_read(db, profile, current_user)


@router.patch("/me", response_model=ClientProfileRead)
def update_client_me(
    payload: ClientProfileUpdate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientProfileRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    update_data = payload.model_dump(exclude_unset=True)

    if "full_name" in update_data:
        profile.full_name = _normalize_optional_text(update_data["full_name"])
    if "selected_city_id" in update_data:
        selected_city_id = update_data["selected_city_id"]
        if selected_city_id is None:
            profile.selected_city_id = None
        else:
            _get_active_city_or_404(db, selected_city_id)
            profile.selected_city_id = selected_city_id

    db.commit()
    db.refresh(profile)
    return _client_profile_to_read(db, profile, current_user)


@router.post("/me/vk-link-codes", response_model=VkLinkCodeRead)
def create_client_vk_link_code(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> VkLinkCodeRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    now = datetime.now(timezone.utc)
    active_codes = db.execute(
        select(VkLinkCode).where(
            VkLinkCode.client_id == profile.id,
            VkLinkCode.status == VkLinkCodeStatus.ACTIVE.value,
            VkLinkCode.expires_at > now,
        )
    ).scalars().all()
    for active_code in active_codes:
        active_code.status = VkLinkCodeStatus.CANCELLED.value

    link_code = VkLinkCode(
        client_id=profile.id,
        code=_generate_vk_link_code(db),
        status=VkLinkCodeStatus.ACTIVE.value,
        expires_at=now + timedelta(seconds=VK_LINK_CODE_TTL_SECONDS),
    )
    db.add(link_code)
    db.commit()
    db.refresh(link_code)
    return _vk_link_code_to_read(link_code)


@router.get("/me/activity", response_model=ActivityFeedRead)
def read_client_activity(
    limit: int = 30,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ActivityFeedRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    return build_client_activity_feed(db, profile.id, limit=limit)


@router.get("/me/subscription", response_model=SubscriptionRead | None)
def read_client_subscription(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> SubscriptionRead | None:
    profile = _get_or_create_client_profile(db, current_user.id)
    subscription = db.execute(
        select(Subscription)
        .where(Subscription.client_id == profile.id)
        .order_by(Subscription.ends_at.desc(), Subscription.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if subscription is None:
        return None
    return SubscriptionRead.model_validate(subscription)


@router.post("/me/payment-requests", response_model=PaymentRequestRead, status_code=status.HTTP_201_CREATED)
def create_client_payment_request(
    payload: PaymentRequestCreate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> PaymentRequestRead:
    profile = _get_current_client_profile_or_404(db, current_user)
    payment_request = PaymentRequest(
        client_id=profile.id,
        amount=payload.amount if payload.amount is not None else Decimal("0.00"),
        status=PaymentRequestStatus.pending.value,
        source=_normalize_optional_text(payload.source) or "web",
        comment=_normalize_optional_text(payload.comment),
    )
    db.add(payment_request)
    db.commit()
    payment_request = _get_owned_payment_request_or_404(db, profile.id, payment_request.id)
    return PaymentRequestRead.model_validate(payment_request)


@router.get("/me/payment-requests", response_model=list[PaymentRequestRead])
def list_client_payment_requests(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[PaymentRequestRead]:
    profile = _get_current_client_profile_or_404(db, current_user)
    payment_requests = db.execute(
        select(PaymentRequest)
        .options(selectinload(PaymentRequest.receipts))
        .where(PaymentRequest.client_id == profile.id)
        .order_by(PaymentRequest.created_at.desc(), PaymentRequest.id.desc())
    ).scalars().all()
    return [PaymentRequestRead.model_validate(payment_request) for payment_request in payment_requests]


@router.get("/me/payment-requests/{payment_request_id}", response_model=PaymentRequestRead)
def read_client_payment_request(
    payment_request_id: int,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> PaymentRequestRead:
    profile = _get_current_client_profile_or_404(db, current_user)
    payment_request = _get_owned_payment_request_or_404(db, profile.id, payment_request_id)
    return PaymentRequestRead.model_validate(payment_request)


@router.post("/me/payment-requests/{payment_request_id}/mark-paid", response_model=PaymentRequestRead)
def mark_client_payment_request_paid(
    payment_request_id: int,
    payload: PaymentRequestMarkPaid,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> PaymentRequestRead:
    profile = _get_current_client_profile_or_404(db, current_user)
    payment_request = _get_owned_payment_request_or_404(db, profile.id, payment_request_id)

    if payment_request.status == PaymentRequestStatus.pending.value:
        payment_request.status = PaymentRequestStatus.paid.value
        payment_request.updated_at = datetime.now(timezone.utc)
    elif payment_request.status == PaymentRequestStatus.paid.value:
        pass
    elif payment_request.status in {PaymentRequestStatus.approved.value, PaymentRequestStatus.rejected.value}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment request cannot be marked as paid",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported payment request status",
        )

    _append_payment_request_comment(payment_request, payload.comment)
    db.commit()
    payment_request = _get_owned_payment_request_or_404(db, profile.id, payment_request.id)
    return PaymentRequestRead.model_validate(payment_request)


@router.post(
    "/me/payment-requests/{payment_request_id}/receipts",
    response_model=PaymentReceiptRead,
    status_code=status.HTTP_201_CREATED,
)
def create_client_payment_receipt(
    payment_request_id: int,
    payload: PaymentReceiptCreate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> PaymentReceiptRead:
    profile = _get_current_client_profile_or_404(db, current_user)
    _get_owned_payment_request_or_404(db, profile.id, payment_request_id)
    receipt = PaymentReceipt(
        payment_request_id=payment_request_id,
        file_url=payload.file_url,
        uploaded_via=_normalize_optional_text(payload.uploaded_via) or "web",
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return PaymentReceiptRead.model_validate(receipt)


@router.get("/catalog/partners", response_model=list[ClientPartnerCatalogItem])
def list_client_catalog_partners(
    city_id: int | None = None,
    city_slug: str | None = None,
    category_slug: str | None = None,
    q: str | None = None,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[ClientPartnerCatalogItem]:
    profile = _get_or_create_client_profile(db, current_user.id)
    resolved_city_id = _resolve_catalog_city_id(db, profile, city_id, city_slug)
    normalized_category_slug = _normalize_optional_text(category_slug)
    normalized_query = _normalize_optional_text(q)

    statement = (
        select(Partner, City.name.label("city_name"))
        .join(City, Partner.city_id == City.id)
        .where(Partner.is_active.is_(True))
        .order_by(Partner.sort_order.asc(), Partner.id.asc())
    )
    if resolved_city_id is not None:
        statement = statement.where(Partner.city_id == resolved_city_id)
    if normalized_category_slug is not None:
        statement = statement.where(Partner.category_slug == normalized_category_slug)
    if normalized_query is not None:
        search = f"%{normalized_query}%"
        statement = statement.where(Partner.name.ilike(search))

    rows = db.execute(statement).all()
    partner_ids = [partner.id for partner, _city_name in rows]
    photos_by_partner = _active_photos_by_partner(db, partner_ids)
    return [
        _partner_to_catalog_item(partner, city_name, photos_by_partner.get(partner.id, []))
        for partner, city_name in rows
    ]


@router.post("/partners/{partner_id}/verify", response_model=ClientVerificationRead)
def create_client_partner_verification(
    partner_id: int,
    payload: ClientCreateVerificationRequest,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientVerificationRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    partner, _city_name = _get_active_partner_row_or_404(db, partner_id)
    offer = _get_active_partner_offer_or_404(db, partner.id, payload.offer_id) if payload.offer_id is not None else None

    now = datetime.now(timezone.utc)
    if not _has_active_subscription(db, profile.id, now):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL,
        )

    existing_session = _get_existing_active_verification(
        db,
        profile.id,
        partner.id,
        offer.id if offer is not None else None,
        now,
    )
    if existing_session is not None:
        return _client_verification_to_read(existing_session, partner.name, offer.title if offer is not None else None)

    session = PrivilegeVerificationSession(
        client_id=profile.id,
        partner_id=partner.id,
        offer_id=offer.id if offer is not None else None,
        code=_generate_verification_code(),
        status=PrivilegeVerificationStatus.active.value,
        source=_normalize_optional_text(payload.source) or "web",
        expires_at=now + timedelta(seconds=VERIFICATION_TTL_SECONDS),
        created_at=now,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _client_verification_to_read(session, partner.name, offer.title if offer is not None else None)


@router.get("/me/verifications", response_model=list[ClientVerificationRead])
def list_client_verifications(
    status: str | None = None,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[ClientVerificationRead]:
    profile = _get_or_create_client_profile(db, current_user.id)
    statement = (
        select(PrivilegeVerificationSession, Partner.name.label("partner_name"), PartnerOffer.title.label("offer_title"))
        .join(Partner, PrivilegeVerificationSession.partner_id == Partner.id)
        .outerjoin(PartnerOffer, PrivilegeVerificationSession.offer_id == PartnerOffer.id)
        .where(PrivilegeVerificationSession.client_id == profile.id)
        .order_by(PrivilegeVerificationSession.created_at.desc(), PrivilegeVerificationSession.id.desc())
    )
    if status is not None:
        statement = statement.where(PrivilegeVerificationSession.status == status)

    return [
        _client_verification_to_read(session, partner_name, offer_title)
        for session, partner_name, offer_title in db.execute(statement).all()
    ]


@router.get("/partners/{partner_id}", response_model=ClientPartnerCatalogItem)
def read_client_partner(
    partner_id: int,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientPartnerCatalogItem:
    del current_user
    partner, city_name = _get_active_partner_row_or_404(db, partner_id)
    return _partner_to_catalog_item(partner, city_name, _active_photos_by_partner(db, [partner.id]).get(partner.id, []))


@router.get("/partners/{partner_id}/offers", response_model=list[ClientPartnerOfferRead])
def list_client_partner_offers(
    partner_id: int,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[ClientPartnerOfferRead]:
    del current_user
    _get_active_partner_row_or_404(db, partner_id)
    offers = db.execute(
        select(PartnerOffer)
        .where(PartnerOffer.partner_id == partner_id, PartnerOffer.is_active.is_(True))
        .order_by(PartnerOffer.sort_order.asc(), PartnerOffer.id.asc())
    ).scalars().all()
    return [_partner_offer_to_read(offer) for offer in offers]


def _get_current_client_profile_or_404(db: Session, current_user: User) -> ClientProfile:
    profile = db.execute(select(ClientProfile).where(ClientProfile.user_id == current_user.id)).scalar_one_or_none()
    if profile is not None:
        return profile
    return _get_or_create_client_profile(db, current_user.id)


def _get_owned_payment_request_or_404(db: Session, client_id: int, payment_request_id: int) -> PaymentRequest:
    payment_request = db.execute(
        select(PaymentRequest)
        .options(selectinload(PaymentRequest.receipts))
        .where(PaymentRequest.id == payment_request_id, PaymentRequest.client_id == client_id)
    ).scalar_one_or_none()
    if payment_request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment request not found")
    return payment_request


def _append_payment_request_comment(payment_request: PaymentRequest, comment: str | None) -> None:
    normalized_comment = _normalize_optional_text(comment)
    if normalized_comment is None:
        return
    if payment_request.comment:
        if payment_request.comment.strip() == normalized_comment:
            return
        payment_request.comment = f"{payment_request.comment}\n\nClient mark-paid comment: {normalized_comment}"
    else:
        payment_request.comment = normalized_comment
    payment_request.updated_at = datetime.now(timezone.utc)


def _get_or_create_client_profile(db: Session, user_id: int) -> ClientProfile:
    profile = db.execute(select(ClientProfile).where(ClientProfile.user_id == user_id)).scalar_one_or_none()
    if profile is not None:
        return profile

    profile = ClientProfile(user_id=user_id, is_active=True, source="web")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _client_profile_to_read(db: Session, profile: ClientProfile, user: User) -> ClientProfileRead:
    selected_city_name = None
    if profile.selected_city_id is not None:
        selected_city_name = db.execute(select(City.name).where(City.id == profile.selected_city_id)).scalar_one_or_none()
    return ClientProfileRead.model_validate(
        {
            "id": profile.id,
            "user_id": profile.user_id,
            "email": user.email,
            "phone": user.phone,
            "full_name": profile.full_name,
            "selected_city_id": profile.selected_city_id,
            "selected_city_name": selected_city_name,
            "vk_user_id": profile.vk_user_id,
            "source": profile.source,
            "is_active": profile.is_active,
        }
    )


def _generate_vk_link_code(db: Session) -> str:
    for _ in range(20):
        code = "".join(secrets.choice(VK_LINK_CODE_ALPHABET) for _ in range(VK_LINK_CODE_LENGTH))
        exists = db.execute(select(VkLinkCode.id).where(VkLinkCode.code == code)).scalar_one_or_none()
        if exists is None:
            return code
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate VK link code",
    )


def _vk_link_code_to_read(link_code: VkLinkCode) -> VkLinkCodeRead:
    expires_at = _ensure_aware_utc(link_code.expires_at)
    ttl_seconds = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    return VkLinkCodeRead(
        code=link_code.code,
        status=link_code.status,
        expires_at=expires_at,
        ttl_seconds=ttl_seconds,
    )


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _has_active_subscription(db: Session, client_id: int, now: datetime) -> bool:
    subscription = db.execute(
        select(Subscription.id)
        .where(
            Subscription.client_id == client_id,
            Subscription.status == SubscriptionStatus.active.value,
            Subscription.starts_at <= now,
            Subscription.ends_at > now,
        )
        .limit(1)
    ).scalar_one_or_none()
    return subscription is not None


def _get_existing_active_verification(
    db: Session,
    client_id: int,
    partner_id: int,
    offer_id: int | None,
    now: datetime,
) -> PrivilegeVerificationSession | None:
    statement = (
        select(PrivilegeVerificationSession)
        .where(
            PrivilegeVerificationSession.client_id == client_id,
            PrivilegeVerificationSession.partner_id == partner_id,
            PrivilegeVerificationSession.status == PrivilegeVerificationStatus.active.value,
            PrivilegeVerificationSession.expires_at > now,
        )
        .order_by(PrivilegeVerificationSession.created_at.desc(), PrivilegeVerificationSession.id.desc())
        .limit(1)
    )
    if offer_id is None:
        statement = statement.where(PrivilegeVerificationSession.offer_id.is_(None))
    else:
        statement = statement.where(PrivilegeVerificationSession.offer_id == offer_id)
    return db.execute(statement).scalar_one_or_none()

def _get_active_city_or_404(db: Session, city_id: int) -> City:
    city = db.execute(select(City).where(City.id == city_id, City.is_active.is_(True))).scalar_one_or_none()
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CITY_NOT_FOUND_DETAIL)
    return city


def _resolve_catalog_city_id(
    db: Session,
    profile: ClientProfile,
    city_id: int | None,
    city_slug: str | None,
) -> int | None:
    if city_id is not None:
        return city_id

    normalized_city_slug = _normalize_optional_text(city_slug)
    if normalized_city_slug is not None:
        city = db.execute(
            select(City).where(City.slug == normalized_city_slug, City.is_active.is_(True))
        ).scalar_one_or_none()
        if city is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CITY_NOT_FOUND_DETAIL)
        return city.id

    return profile.selected_city_id


def _get_active_partner_row_or_404(db: Session, partner_id: int) -> tuple[Partner, str | None]:
    row = db.execute(
        select(Partner, City.name.label("city_name"))
        .join(City, Partner.city_id == City.id)
        .where(Partner.id == partner_id, Partner.is_active.is_(True))
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PARTNER_NOT_FOUND_DETAIL)
    partner, city_name = row
    return partner, city_name


def _get_active_partner_offer_or_404(db: Session, partner_id: int, offer_id: int) -> PartnerOffer:
    offer = db.execute(
        select(PartnerOffer).where(
            PartnerOffer.id == offer_id,
            PartnerOffer.partner_id == partner_id,
            PartnerOffer.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=OFFER_NOT_FOUND_DETAIL)
    return offer


def _generate_verification_code(length: int = 6) -> str:
    return "".join(secrets.choice(VERIFICATION_CODE_ALPHABET) for _ in range(length))


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _ttl_seconds(expires_at: datetime) -> int | None:
    seconds = int((_as_aware_utc(expires_at) - datetime.now(timezone.utc)).total_seconds())
    return max(seconds, 0)


def _client_verification_to_read(
    session: PrivilegeVerificationSession,
    partner_name: str | None,
    offer_title: str | None,
) -> ClientVerificationRead:
    return ClientVerificationRead.model_validate(
        {
            "id": session.id,
            "client_id": session.client_id,
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
            "subscription_required": False,
        }
    )


def _active_photos_by_partner(db: Session, partner_ids: list[int]) -> dict[int, list[ClientPartnerPhotoRead]]:
    if not partner_ids:
        return {}
    photos = db.execute(
        select(PartnerPhoto)
        .where(PartnerPhoto.partner_id.in_(partner_ids), PartnerPhoto.is_active.is_(True))
        .order_by(PartnerPhoto.partner_id.asc(), PartnerPhoto.sort_order.asc(), PartnerPhoto.created_at.asc())
    ).scalars().all()
    result: dict[int, list[ClientPartnerPhotoRead]] = {}
    for photo in photos:
        result.setdefault(photo.partner_id, []).append(
            ClientPartnerPhotoRead.model_validate(
                {
                    "id": photo.id,
                    "url": photo.url,
                    "alt_text": photo.alt_text,
                    "sort_order": photo.sort_order,
                    "created_at": photo.created_at,
                }
            )
        )
    return result


def _partner_to_catalog_item(
    partner: Partner,
    city_name: str | None,
    photos: list[ClientPartnerPhotoRead] | None = None,
) -> ClientPartnerCatalogItem:
    return ClientPartnerCatalogItem.model_validate(
        {
            "id": partner.id,
            "city_id": partner.city_id,
            "city_name": city_name,
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
            "is_verified": partner.is_verified,
            "photos": photos or [],
        }
    )


def _partner_offer_to_read(offer: PartnerOffer) -> ClientPartnerOfferRead:
    return ClientPartnerOfferRead.model_validate(
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
            "sort_order": offer.sort_order,
        }
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
