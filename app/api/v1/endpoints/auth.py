from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import AdminUser, User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UnifiedTokenResponse,
    UnifiedUserRead,
    UserLoginRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.get("/user-me", response_model=UnifiedUserRead)
def read_user_me(user: User = Depends(get_current_user)) -> User:
    return user
