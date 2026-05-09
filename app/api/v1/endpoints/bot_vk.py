from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_bot_api_token
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.city import City
from app.models.client import ClientProfile, VkLinkCode, VkLinkCodeStatus
from app.models.user import User, UserRole
from app.schemas.auth import UnifiedUserRead
from app.schemas.vk import (
    VkExchangeLinkCodeRequest,
    VkExchangeTokenResponse,
    VkOnboardClientProfileRead,
    VkOnboardClientRequest,
    VkOnboardClientResponse,
    VkOnboardClientUserRead,
    VkTokenRequest,
)

router = APIRouter(prefix="/bot/vk", tags=["bot-vk"])


@router.post("/exchange-link-code", response_model=VkExchangeTokenResponse)
def exchange_vk_link_code(
    payload: VkExchangeLinkCodeRequest,
    _: None = Depends(require_bot_api_token),
    db: Session = Depends(get_db),
) -> VkExchangeTokenResponse:
    vk_user_id = _normalize_required(payload.vk_user_id, "VK user ID is required")
    code_value = payload.code.strip().upper()
    if not code_value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link code not found")

    link_code = db.execute(select(VkLinkCode).where(VkLinkCode.code == code_value)).scalar_one_or_none()
    if link_code is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link code not found")
    if link_code.status != VkLinkCodeStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link code is not active")

    now = datetime.now(timezone.utc)
    if _ensure_aware_utc(link_code.expires_at) <= now:
        link_code.status = VkLinkCodeStatus.EXPIRED.value
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link code expired")

    profile = db.execute(
        select(ClientProfile)
        .options(joinedload(ClientProfile.user))
        .where(ClientProfile.id == link_code.client_id)
    ).scalar_one_or_none()
    if profile is None or profile.user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client user not found")
    user = profile.user
    if not user.is_active or user.role != UserRole.CLIENT.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client user not found")

    existing_profile_id = db.execute(
        select(ClientProfile.id).where(
            ClientProfile.vk_user_id == vk_user_id,
            ClientProfile.id != profile.id,
        )
    ).scalar_one_or_none()
    if existing_profile_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VK user is already linked")

    profile.vk_user_id = vk_user_id
    link_code.status = VkLinkCodeStatus.USED.value
    link_code.used_at = now
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/token", response_model=VkExchangeTokenResponse)
def create_vk_user_token(
    payload: VkTokenRequest,
    _: None = Depends(require_bot_api_token),
    db: Session = Depends(get_db),
) -> VkExchangeTokenResponse:
    vk_user_id = _normalize_required(payload.vk_user_id, "VK user ID is required")
    profile = db.execute(
        select(ClientProfile)
        .options(joinedload(ClientProfile.user))
        .where(ClientProfile.vk_user_id == vk_user_id)
    ).scalar_one_or_none()
    if profile is None or profile.user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VK user is not linked")
    user = profile.user
    if not user.is_active or user.role != UserRole.CLIENT.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VK user is not linked")
    return _token_response(user)


@router.post("/onboard-client", response_model=VkOnboardClientResponse)
def onboard_vk_client(
    payload: VkOnboardClientRequest,
    _: None = Depends(require_bot_api_token),
    db: Session = Depends(get_db),
) -> VkOnboardClientResponse:
    vk_user_id = _normalize_required(payload.vk_user_id, "vk_user_id must not be empty")
    selected_city_id = _resolve_selected_city_id(db, payload.selected_city_slug)

    profile = db.execute(
        select(ClientProfile)
        .options(joinedload(ClientProfile.user))
        .where(ClientProfile.vk_user_id == vk_user_id)
    ).scalar_one_or_none()
    if profile is not None:
        user = profile.user
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client user not found")
        if user.role != UserRole.CLIENT.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Linked user is not a client")
        if selected_city_id is not None:
            profile.selected_city_id = selected_city_id
            db.commit()
            db.refresh(profile)
            db.refresh(user)
        return _onboard_response(user, profile, is_new=False)

    user = User(
        email=None,
        phone=None,
        password_hash=None,
        role=UserRole.CLIENT.value,
        is_active=True,
    )
    db.add(user)
    db.flush()

    profile = ClientProfile(
        user_id=user.id,
        vk_user_id=vk_user_id,
        selected_city_id=selected_city_id,
        full_name=_normalize_optional_text(payload.full_name),
        source=_normalize_optional_text(payload.source) or "vk",
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    return _onboard_response(user, profile, is_new=True)


def _token_response(user: User) -> VkExchangeTokenResponse:
    return VkExchangeTokenResponse(
        access_token=create_access_token(f"user:{user.id}"),
        user=UnifiedUserRead.model_validate(user),
    )


def _onboard_response(user: User, profile: ClientProfile, is_new: bool) -> VkOnboardClientResponse:
    return VkOnboardClientResponse(
        access_token=create_access_token(f"user:{user.id}"),
        user=VkOnboardClientUserRead.model_validate(user),
        client=VkOnboardClientProfileRead.model_validate(profile),
        is_new=is_new,
        password_setup_required=user.password_hash is None,
    )


def _resolve_selected_city_id(db: Session, selected_city_slug: str | None) -> int | None:
    normalized_slug = _normalize_optional_text(selected_city_slug)
    if normalized_slug is None:
        return None
    city_id = db.execute(
        select(City.id).where(City.slug == normalized_slug, City.is_active.is_(True))
    ).scalar_one_or_none()
    if city_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return int(city_id)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_required(value: str, detail: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    return normalized


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
