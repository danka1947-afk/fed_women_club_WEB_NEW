from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_client
from app.core.categories import get_women_club_categories
from app.db.session import get_db
from app.models.city import City
from app.models.category import Category
from app.models.client import ClientProfile, VkLinkCode, VkLinkCodeStatus
from app.models.partner import OfferPhoto, Partner, PartnerOffer, PartnerPhoto
from app.models.payment import PaymentReceipt, PaymentRequest, PaymentRequestStatus, Subscription, SubscriptionStatus
from app.models.verification import PrivilegeVerificationSession, PrivilegeVerificationStatus
from app.models.user import User
from app.schemas.activity import ActivityFeedRead
from app.schemas.client import (
    ClientSiteCredentialsRead,
    ClientCityResponse,
    ClientCreateVerificationRequest,
    ClientPartnerCatalogItem,
    ClientPartnerCategoryRead,
    ClientPartnerOfferRead,
    ClientPartnerPhotoRead,
    ClientProfileRead,
    ClientProfileUpdate,
    ClientSavingsItemRead,
    ClientSavingsPeriodRead,
    ClientSavingsRead,
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
from app.services.offer_savings import calculate_offer_saving_snapshot
from app.services.site_credentials import (
    decrypt_site_password,
    ensure_client_site_credentials,
)
from app.services.privilege_verifications import (
    PRIVILEGE_VERIFICATION_TTL_SECONDS,
    apply_verification_status_filter,
    as_aware_utc,
    normalize_expired_verifications,
    ttl_seconds,
)

router = APIRouter(prefix="/clients", tags=["clients"])

CITY_NOT_FOUND_DETAIL = "City not found"
PARTNER_NOT_FOUND_DETAIL = "Partner not found"
OFFER_NOT_FOUND_DETAIL = "Offer not found"
ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL = "Active subscription required"
VERIFICATION_CODE_ALPHABET = string.digits
PRIVILEGE_QR_PAYLOAD_PREFIX = "bloomclub:privilege:"
VK_LINK_CODE_TTL_SECONDS = 10 * 60
VK_LINK_CODE_LENGTH = 8
VK_LINK_CODE_ALPHABET = string.ascii_uppercase + string.digits
CATEGORY_DISPLAY_BY_SLUG = {item["slug"]: item["title"] for item in get_women_club_categories()}


@router.get("/me", response_model=ClientProfileRead)
def read_client_me(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientProfileRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    return _client_profile_to_read(db, profile, current_user)




@router.get("/me/site-credentials", response_model=ClientSiteCredentialsRead)
def read_client_site_credentials(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientSiteCredentialsRead:
    _get_or_create_client_profile(db, current_user.id)
    generated_credentials, plain_password = ensure_client_site_credentials(db, current_user)
    if generated_credentials:
        db.commit()
        db.refresh(current_user)
    if not current_user.site_login or (plain_password is None and not current_user.encrypted_site_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site credentials are not available",
        )
    site_password = plain_password or decrypt_site_password(current_user.encrypted_site_password)
    return ClientSiteCredentialsRead(site_login=current_user.site_login, site_password=site_password)


@router.get("/cities", response_model=list[ClientCityResponse])
def list_client_cities(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[City]:
    _ = current_user
    result = db.execute(
        select(City)
        .where(City.is_active.is_(True))
        .order_by(City.sort_order.asc(), City.name.asc(), City.id.asc())
    )
    return list(result.scalars().all())


@router.patch("/me", response_model=ClientProfileRead)
def update_client_me(
    payload: ClientProfileUpdate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientProfileRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and "full_name" not in update_data:
        update_data["full_name"] = update_data["name"]

    if "full_name" in update_data:
        profile.full_name = _normalize_required_name(update_data["full_name"])

    city_text = _normalize_optional_text(update_data.get("custom_city"))
    if city_text is None:
        city_text = _normalize_optional_text(update_data.get("city"))

    resolved_city_id = _resolve_city_for_profile_update(
        db,
        update_data.get("selected_city_id" if "selected_city_id" in update_data else "city_id"),
        update_data.get("city_slug"),
        keep_current=profile.selected_city_id,
    )
    if any(field in update_data for field in ("selected_city_id", "city_id", "city_slug")):
        profile.selected_city_id = resolved_city_id

    if city_text is not None:
        resolved_text_city_id = _resolve_city_id_by_name(db, city_text)
        profile.custom_city = city_text
        if resolved_text_city_id is not None:
            profile.selected_city_id = resolved_text_city_id
    elif any(field in update_data for field in ("city", "custom_city")):
        profile.custom_city = None

    if "phone" in update_data:
        normalized_phone = _normalize_phone(update_data["phone"])
        _ensure_unique_user_phone(db, normalized_phone, current_user.id)
        current_user.phone = normalized_phone

    if "contact_email" in update_data:
        profile.contact_email = _normalize_email(update_data["contact_email"])
    elif "email" in update_data:
        normalized_email = _normalize_email(update_data["email"])
        _ensure_unique_user_email(db, normalized_email, current_user.id)
        profile.contact_email = normalized_email
        current_user.email = normalized_email

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


@router.get("/me/subscription", response_model=SubscriptionRead)
def read_client_subscription(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> SubscriptionRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    now = datetime.now(timezone.utc)
    subscription = db.execute(
        select(Subscription)
        .where(
            Subscription.client_id == profile.id,
            Subscription.status == SubscriptionStatus.active.value,
            Subscription.starts_at <= now,
            Subscription.ends_at > now,
        )
        .order_by(Subscription.ends_at.desc(), Subscription.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if subscription is None:
        return SubscriptionRead(
            status="inactive",
            is_active=False,
            expires_at=None,
            end_date=None,
            amount=Decimal("349.00"),
        )

    return SubscriptionRead(
        id=subscription.id,
        client_id=subscription.client_id,
        status=SubscriptionStatus.active.value,
        starts_at=subscription.starts_at,
        ends_at=subscription.ends_at,
        source_payment_request_id=subscription.source_payment_request_id,
        is_active=True,
        expires_at=subscription.ends_at,
        end_date=subscription.ends_at,
        amount=Decimal("349.00"),
    )


@router.post("/me/payment-requests", response_model=PaymentRequestRead, status_code=status.HTTP_201_CREATED)
def create_client_payment_request(
    payload: PaymentRequestCreate | None = None,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> PaymentRequestRead:
    profile = _get_current_client_profile_or_404(db, current_user)
    payload = payload or PaymentRequestCreate()
    payment_request = PaymentRequest(
        client_id=profile.id,
        amount=payload.amount if payload.amount is not None else Decimal("349.00"),
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
    payload: PaymentRequestMarkPaid | None = None,
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

    _append_payment_request_comment(payment_request, payload.comment if payload is not None else None)
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
        .options(selectinload(Partner.categories))
        .where(Partner.is_active.is_(True))
        .order_by(Partner.sort_order.asc(), Partner.id.asc())
    )
    if resolved_city_id is not None:
        statement = statement.where(Partner.city_id == resolved_city_id)
    if normalized_category_slug is not None:
        statement = statement.where(
            Partner.categories.any(Category.slug == normalized_category_slug) | (Partner.category_slug == normalized_category_slug)
        )
    if normalized_query is not None:
        search = f"%{normalized_query}%"
        statement = statement.where(Partner.name.ilike(search))

    rows = db.execute(statement).all()
    partner_ids = [partner.id for partner, _city_name in rows]
    photos_by_partner = _active_photos_by_partner(db, partner_ids)
    return [
        _partner_to_catalog_item(
            partner,
            city_name,
            photos_by_partner.get(partner.id, []),
        )
        for partner, city_name in rows
    ]


@router.post("/partners/{partner_id}/verify", response_model=ClientVerificationRead)
def create_client_partner_verification(
    partner_id: int,
    payload: ClientCreateVerificationRequest | None = None,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientVerificationRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    partner, _city_name = _get_active_partner_row_or_404(db, partner_id)
    request_payload = payload or ClientCreateVerificationRequest()
    offer = _resolve_partner_offer_for_verification(db, partner.id, request_payload.offer_id)

    now = datetime.now(timezone.utc)
    if not _has_active_subscription(db, profile.id, now):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ACTIVE_SUBSCRIPTION_REQUIRED_DETAIL,
        )

    normalize_expired_verifications(db, now=now, client_id=profile.id, partner_id=partner.id)

    session = PrivilegeVerificationSession(
        client_id=profile.id,
        partner_id=partner.id,
        offer_id=offer.id if offer is not None else None,
        code=_generate_verification_code(),
        token=_generate_unique_privilege_session_token(db),
        status=PrivilegeVerificationStatus.active.value,
        source=_normalize_optional_text(request_payload.source) or "web",
        expires_at=now + timedelta(seconds=PRIVILEGE_VERIFICATION_TTL_SECONDS),
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
    now = datetime.now(timezone.utc)
    normalize_expired_verifications(db, now=now, client_id=profile.id)
    statement = (
        select(PrivilegeVerificationSession, Partner.name.label("partner_name"), PartnerOffer.title.label("offer_title"))
        .join(Partner, PrivilegeVerificationSession.partner_id == Partner.id)
        .outerjoin(PartnerOffer, PrivilegeVerificationSession.offer_id == PartnerOffer.id)
        .where(PrivilegeVerificationSession.client_id == profile.id)
        .order_by(PrivilegeVerificationSession.created_at.desc(), PrivilegeVerificationSession.id.desc())
    )
    statement = apply_verification_status_filter(statement, status, now=now)

    return [
        _client_verification_to_read(session, partner_name, offer_title)
        for session, partner_name, offer_title in db.execute(statement).all()
    ]


@router.get("/me/savings", response_model=ClientSavingsRead)
def read_client_savings(
    from_date: date | None = None,
    to_date: date | None = None,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientSavingsRead:
    profile = _get_or_create_client_profile(db, current_user.id)
    statement = (
        select(PrivilegeVerificationSession, Partner.name.label("partner_name"), PartnerOffer.title.label("offer_title"))
        .join(Partner, PrivilegeVerificationSession.partner_id == Partner.id)
        .outerjoin(PartnerOffer, PrivilegeVerificationSession.offer_id == PartnerOffer.id)
        .where(
            PrivilegeVerificationSession.client_id == profile.id,
            PrivilegeVerificationSession.status == PrivilegeVerificationStatus.confirmed.value,
        )
    )
    if from_date is not None:
        statement = statement.where(PrivilegeVerificationSession.confirmed_at >= datetime.combine(from_date, time.min, tzinfo=timezone.utc))
    if to_date is not None:
        statement = statement.where(PrivilegeVerificationSession.confirmed_at <= datetime.combine(to_date, time.max, tzinfo=timezone.utc))
    statement = statement.order_by(PrivilegeVerificationSession.confirmed_at.desc(), PrivilegeVerificationSession.id.desc())
    items: list[ClientSavingsItemRead] = []
    total = Decimal("0.00")
    for session, partner_name, offer_title in db.execute(statement).all():
        base_price = session.saving_base_price
        final_price = session.saving_final_price
        discount_percent = session.saving_discount_percent
        saving_amount = session.saving_amount
        used_at = session.saving_used_at or session.confirmed_at
        if saving_amount is None:
            base_price, final_price, discount_percent, saving_amount = _compute_saving_from_offer(session.offer)
        total += saving_amount
        items.append(ClientSavingsItemRead(
            id=session.id, used_at=used_at, partner_id=session.partner_id, partner_name=session.saving_partner_name or partner_name,
            offer_id=session.offer_id, offer_title=session.saving_offer_title or offer_title, base_price=base_price,
            final_price=final_price, discount_percent=discount_percent, saving_amount=saving_amount,
        ))
    return ClientSavingsRead(
        total_saving_amount=total,
        period=ClientSavingsPeriodRead(from_date=from_date.isoformat() if from_date else None, to_date=to_date.isoformat() if to_date else None),
        items=items,
    )


@router.get("/partners/{partner_id}", response_model=ClientPartnerCatalogItem)
def read_client_partner(
    partner_id: int,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ClientPartnerCatalogItem:
    del current_user
    partner, city_name = _get_active_partner_row_or_404(db, partner_id)
    return _partner_to_catalog_item(
        partner,
        city_name,
        _active_photos_by_partner(db, [partner.id]).get(partner.id, []),
    )


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
    photos_by_offer = _active_photos_by_offer(db, [offer.id for offer in offers])
    return [_partner_offer_to_read(offer, photos_by_offer.get(offer.id, [])) for offer in offers]


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


def _compute_saving_from_offer(offer: PartnerOffer | None) -> tuple[Decimal | None, Decimal | None, Decimal | None, Decimal]:
    snapshot = calculate_offer_saving_snapshot(offer)
    return snapshot.regular_price, snapshot.club_price, snapshot.discount_percent, snapshot.saving_amount


def _client_profile_to_read(db: Session, profile: ClientProfile, user: User) -> ClientProfileRead:
    selected_city_name = None
    if profile.selected_city_id is not None:
        selected_city_name = db.execute(select(City.name).where(City.id == profile.selected_city_id)).scalar_one_or_none()
    city_name = profile.custom_city or selected_city_name
    return ClientProfileRead.model_validate(
        {
            "id": profile.id,
            "user_id": profile.user_id,
            "email": user.email,
            "phone": user.phone,
            "contact_email": profile.contact_email,
            "full_name": profile.full_name,
            "selected_city_id": profile.selected_city_id,
            "selected_city_name": selected_city_name,
            "city": city_name,
            "custom_city": profile.custom_city,
            "city_name": city_name,
            "vk_user_id": profile.vk_user_id,
            "site_login": user.site_login,
            "site_password_masked": "*****" if user.encrypted_site_password else None,
            "site_password_available": bool(user.encrypted_site_password),
            "source": profile.source,
            "is_active": profile.is_active,
        }
    )


def _ensure_unique_user_phone(db: Session, phone: str | None, current_user_id: int) -> None:
    if phone is None:
        return
    existing_id = db.execute(select(User.id).where(User.phone == phone, User.id != current_user_id)).scalar_one_or_none()
    if existing_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone is already used")


def _ensure_unique_user_email(db: Session, email: str | None, current_user_id: int) -> None:
    if email is None:
        return
    existing_id = db.execute(
        select(User.id).where(func.lower(User.email) == email.lower(), User.id != current_user_id)
    ).scalar_one_or_none()
    if existing_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already used")


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
    expires_at = as_aware_utc(link_code.expires_at)
    ttl_seconds = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    return VkLinkCodeRead(
        code=link_code.code,
        status=link_code.status,
        expires_at=expires_at,
        ttl_seconds=ttl_seconds,
    )


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


def _get_active_partner_row_or_404(
    db: Session,
    partner_id: int,
) -> tuple[Partner, str | None]:
    row = db.execute(
        select(Partner, City.name.label("city_name"))
        .join(City, Partner.city_id == City.id)
        .options(selectinload(Partner.categories))
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


def _get_first_active_partner_offer(db: Session, partner_id: int) -> PartnerOffer | None:
    return db.execute(
        select(PartnerOffer)
        .where(PartnerOffer.partner_id == partner_id, PartnerOffer.is_active.is_(True))
        .order_by(PartnerOffer.sort_order.asc(), PartnerOffer.id.asc())
        .limit(1)
    ).scalar_one_or_none()


def _resolve_partner_offer_for_verification(db: Session, partner_id: int, offer_id: int | None) -> PartnerOffer | None:
    if offer_id is not None:
        return _get_active_partner_offer_or_404(db, partner_id, offer_id)
    return _get_first_active_partner_offer(db, partner_id)


def _generate_verification_code(length: int = 6) -> str:
    return "".join(secrets.choice(VERIFICATION_CODE_ALPHABET) for _ in range(length))


def _generate_unique_privilege_session_token(db: Session) -> str:
    for _ in range(20):
        token = secrets.token_urlsafe(32)
        exists = db.execute(
            select(PrivilegeVerificationSession.id).where(PrivilegeVerificationSession.token == token)
        ).scalar_one_or_none()
        if exists is None:
            return token
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate privilege session token",
    )


def _privilege_qr_payload(token: str | None) -> str | None:
    if not token:
        return None
    return f"{PRIVILEGE_QR_PAYLOAD_PREFIX}{token}"


def _client_verification_to_read(
    session: PrivilegeVerificationSession,
    partner_name: str | None,
    offer_title: str | None,
) -> ClientVerificationRead:
    return ClientVerificationRead.model_validate(
        {
            "id": session.id,
            "session_id": session.id,
            "client_id": session.client_id,
            "partner_id": session.partner_id,
            "partner_name": partner_name,
            "offer_id": session.offer_id,
            "offer_title": offer_title,
            "code": session.code,
            "display_code": session.code,
            "token": session.token,
            "qr_payload": _privilege_qr_payload(session.token),
            "status": session.status,
            "source": session.source,
            "expires_at": session.expires_at,
            "confirmed_at": session.confirmed_at,
            "created_at": session.created_at,
            "ttl_seconds": ttl_seconds(session.expires_at),
            "subscription_required": False,
        }
    )


def _active_photos_by_partner(db: Session, partner_ids: list[int]) -> dict[int, list[ClientPartnerPhotoRead]]:
    if not partner_ids:
        return {}
    photos = db.execute(
        select(PartnerPhoto)
        .where(PartnerPhoto.partner_id.in_(partner_ids), PartnerPhoto.is_active.is_(True))
        .order_by(PartnerPhoto.partner_id.asc(), PartnerPhoto.sort_order.asc(), PartnerPhoto.id.asc())
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
    active_categories = sorted(
        [category for category in partner.categories if category.is_active],
        key=lambda c: (c.sort_order, c.name.lower(), c.id),
    )
    first = active_categories[0] if active_categories else None
    photo_url = photos[0].url if photos else None
    return ClientPartnerCatalogItem.model_validate(
        {
            "id": partner.id,
            "city_id": partner.city_id,
            "city_name": _humanize_display_text(city_name),
            "category_id": first.id if first is not None else None,
            "category_name": _display_category_name(
                first.name if first is not None else None,
                first.slug if first is not None else partner.category_slug,
            ),
            "category_slug": first.slug if first is not None else partner.category_slug,
            "category": (
                ClientPartnerCategoryRead(
                    id=first.id,
                    name=_display_category_name(first.name, first.slug),
                    slug=first.slug,
                )
                if first is not None
                else None
            ),
            "categories": [
                ClientPartnerCategoryRead(id=c.id, name=_display_category_name(c.name, c.slug), slug=c.slug)
                for c in active_categories
            ],
            "category_ids": [c.id for c in active_categories],
            "category_slugs": [c.slug for c in active_categories],
            "name": partner.name,
            "description": partner.description,
            "address": partner.address,
            "phone": partner.phone,
            "website_url": partner.website_url,
            "social_url": partner.social_url,
            "instagram_url": partner.instagram_url,
            "vk_url": partner.vk_url,
            "telegram_url": partner.telegram_url,
            "whatsapp_url": partner.whatsapp_url,
            "map_url": partner.map_url,
            "working_hours": partner.working_hours,
            "logo_url": partner.logo_url,
            "cover_url": partner.cover_url,
            "photo_url": photo_url,
            "is_verified": partner.is_verified,
            "photos": photos or [],
        }
    )


def _active_photos_by_offer(db: Session, offer_ids: list[int]) -> dict[int, list[dict[str, object]]]:
    if not offer_ids:
        return {}
    photos = db.execute(
        select(OfferPhoto)
        .where(OfferPhoto.offer_id.in_(offer_ids), OfferPhoto.is_active.is_(True))
        .order_by(OfferPhoto.offer_id.asc(), OfferPhoto.sort_order.asc(), OfferPhoto.id.asc())
    ).scalars().all()
    result: dict[int, list[dict[str, object]]] = {}
    for photo in photos:
        result.setdefault(photo.offer_id, []).append(
            {"id": photo.id, "url": photo.url, "alt_text": photo.alt_text, "sort_order": photo.sort_order}
        )
    return result


def _humanize_display_text(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    return normalized[0].upper() + normalized[1:] if normalized else normalized


def _display_category_name(name: str | None, slug: str | None) -> str | None:
    normalized_slug = _normalize_optional_text(slug)
    if normalized_slug is not None and normalized_slug in CATEGORY_DISPLAY_BY_SLUG:
        return CATEGORY_DISPLAY_BY_SLUG[normalized_slug]
    return _humanize_display_text(name)


def _partner_offer_to_read(offer: PartnerOffer, photos: list[dict[str, object]] | None = None) -> ClientPartnerOfferRead:
    photos_payload = photos or []
    photo_url = str(photos_payload[0]["url"]) if photos_payload else None
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
            "photo_url": photo_url,
            "photos": photos_payload,
            "sort_order": offer.sort_order,
        }
    )




def _resolve_city_id_by_name(db: Session, city_name: str) -> int | None:
    normalized_city_name = _normalize_optional_text(city_name)
    if normalized_city_name is None:
        return None
    return db.execute(
        select(City.id).where(City.name.ilike(normalized_city_name), City.is_active.is_(True)).limit(1)
    ).scalar_one_or_none()

def _resolve_city_for_profile_update(
    db: Session,
    city_id: int | None,
    city_slug: str | None,
    keep_current: int | None,
) -> int | None:
    if city_id is not None:
        _get_active_city_or_404(db, city_id)
        return city_id
    normalized_slug = _normalize_optional_text(city_slug)
    if normalized_slug is not None:
        city = db.execute(select(City).where(City.slug == normalized_slug, City.is_active.is_(True))).scalar_one_or_none()
        if city is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=CITY_NOT_FOUND_DETAIL)
        return city.id
    if city_slug is not None:
        return None
    return keep_current


def _normalize_email(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    return normalized.lower()


def _normalize_phone(value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None
    if normalized.startswith("8") and len(normalized) == 11 and normalized[1:].isdigit():
        normalized = "+7" + normalized[1:]
    if len(normalized) > 64:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone is too long")
    return normalized


def _normalize_required_name(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name must not be empty")
    if len(normalized) > 255:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is too long")
    return normalized

def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
