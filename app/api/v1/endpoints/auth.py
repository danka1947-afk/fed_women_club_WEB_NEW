from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    hash_password_setup_token,
    verify_password,
)
from app.db.session import get_db
from app.models.client import ClientPasswordSetupToken
from app.models.user import AdminUser, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordSetupCompleteRequest,
    PasswordSetupCompleteResponse,
    UnifiedTokenResponse,
    UnifiedUserRead,
    UserLoginRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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
