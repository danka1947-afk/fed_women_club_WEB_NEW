from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_bot_api_token
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.client import ClientProfile, VkLinkCode, VkLinkCodeStatus
from app.models.user import User, UserRole
from app.schemas.auth import UnifiedUserRead
from app.schemas.vk import VkExchangeLinkCodeRequest, VkExchangeTokenResponse, VkTokenRequest

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


def _token_response(user: User) -> VkExchangeTokenResponse:
    return VkExchangeTokenResponse(
        access_token=create_access_token(f"user:{user.id}"),
        user=UnifiedUserRead.model_validate(user),
    )


def _normalize_required(value: str, detail: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    return normalized


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
