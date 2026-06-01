from __future__ import annotations

from datetime import datetime, timezone

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    hash_password_setup_token,
    verify_password,
)
from app.db.session import get_db
from app.models.client import ClientPasswordSetupToken
from app.models.client import ClientProfile
from app.models.user import AdminUser, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordSetupCompleteRequest,
    PasswordSetupCompleteResponse,
    UnifiedTokenResponse,
    UnifiedUserRead,
    UserLoginRequest,
    VkMiniAppLoginResponse,
)
from app.services.vk_miniapp_auth import (
    extract_vk_user_id,
    parse_launch_params,
    validate_vk_ts_freshness,
    verify_vk_miniapp_signature,
)

router = APIRouter(prefix="/auth", tags=["auth"])


VK_MINIAPP_LOGIN_HANDLER = "vk-miniapp-login-v2"
VK_MINIAPP_ENTRYPOINT = "fed_women_club_WEB"
PASSWORD_SETUP_PURPOSE = "vk_onboarding_password_setup"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    result = db.execute(select(AdminUser).where(AdminUser.email == payload.email.lower()))
    admin = result.scalar_one_or_none()

    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin user")

    token = create_access_token(str(admin.id))
    return LoginResponse(access_token=token, user=admin)


@router.post("/user-login", response_model=UnifiedTokenResponse)
def user_login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> UnifiedTokenResponse:
    login_value = payload.login.strip()
    email_value = login_value.lower()
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    result = db.execute(
        select(User).where(
            or_(
                func.lower(User.email) == email_value,
                User.phone == login_value,
            )
        )
    )
    user = result.scalars().first()

    if user is None or not user.is_active or not user.password_hash:
        raise unauthorized
    if not verify_password(payload.password, user.password_hash):
        raise unauthorized

    token = create_access_token(f"user:{user.id}")
    return UnifiedTokenResponse(access_token=token, user=user)


def _missing_launch_params_response() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "launch_params are required",
            "handler": VK_MINIAPP_LOGIN_HANDLER,
            "entrypoint": VK_MINIAPP_ENTRYPOINT,
        },
    )


def _stringify_params(params: dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in params.items() if value is not None}


def _extract_vk_miniapp_params(payload: Any) -> dict[str, str] | None:
    if not isinstance(payload, dict) or not payload:
        return None

    launch_params = payload.get("launch_params") or payload.get("launchParams")
    if isinstance(launch_params, str) and launch_params.strip():
        return parse_launch_params(launch_params)

    params = payload.get("params")
    if isinstance(params, dict) and params:
        return _stringify_params(params)

    if "sign" in payload and any(key.startswith("vk_") for key in payload):
        return _stringify_params(payload)

    return None


def _build_vk_miniapp_full_name(params: dict[str, str]) -> str | None:
    parts = [
        (params.get("vk_first_name") or params.get("first_name") or "").strip(),
        (params.get("vk_last_name") or params.get("last_name") or "").strip(),
    ]
    full_name = " ".join(part for part in parts if part)
    return full_name or None


def _get_or_create_vk_client_profile(
    db: Session,
    vk_user_id: str,
    params: dict[str, str],
) -> ClientProfile:
    profile = db.execute(
        select(ClientProfile)
        .options(joinedload(ClientProfile.user))
        .where(ClientProfile.vk_user_id == vk_user_id)
    ).scalar_one_or_none()
    if profile is not None:
        return profile

    user = User(role=UserRole.CLIENT.value, is_active=True)
    db.add(user)
    db.flush()

    profile = ClientProfile(
        user_id=user.id,
        vk_user_id=vk_user_id,
        full_name=_build_vk_miniapp_full_name(params),
        source="vk-miniapp",
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/vk-miniapp-login", response_model=VkMiniAppLoginResponse)
def vk_miniapp_login(
    payload: Any = Body(default=None),
    db: Session = Depends(get_db),
) -> VkMiniAppLoginResponse | JSONResponse:
    params = _extract_vk_miniapp_params(payload)
    if params is None:
        return _missing_launch_params_response()

    verify_vk_miniapp_signature(params)
    validate_vk_ts_freshness(params)
    vk_user_id = extract_vk_user_id(params)

    profile = _get_or_create_vk_client_profile(db, vk_user_id, params)
    user = profile.user
    if user is None or not user.is_active or user.role != UserRole.CLIENT.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client user is inactive or invalid")

    return VkMiniAppLoginResponse(
        access_token=create_access_token(f"user:{user.id}"),
        user=UnifiedUserRead.model_validate(user),
        client=profile,
    )


@router.post("/password-setup/complete", response_model=PasswordSetupCompleteResponse)
def complete_password_setup(
    payload: PasswordSetupCompleteRequest,
    db: Session = Depends(get_db),
) -> PasswordSetupCompleteResponse:
    token = payload.token.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password setup link",
        )
    if payload.password_confirm is not None and payload.password != payload.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 8 characters",
        )

    now = datetime.now(timezone.utc)
    setup_token = db.execute(
        select(ClientPasswordSetupToken).where(
            ClientPasswordSetupToken.token_hash == hash_password_setup_token(token),
            ClientPasswordSetupToken.purpose == PASSWORD_SETUP_PURPOSE,
            ClientPasswordSetupToken.used_at.is_(None),
        )
    ).scalar_one_or_none()

    if setup_token is None or _ensure_aware_utc(setup_token.expires_at) <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password setup link",
        )

    user = db.get(User, setup_token.user_id)
    if user is None or not user.is_active or user.role != UserRole.CLIENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password setup link",
        )

    user.password_hash = hash_password(payload.password)
    setup_token.used_at = now
    db.commit()

    return PasswordSetupCompleteResponse(
        ok=True,
        login=user.email or user.phone,
        message="Password has been set",
    )


@router.get("/user-me", response_model=UnifiedUserRead)
def read_user_me(user: User = Depends(get_current_user)) -> User:
    return user


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
