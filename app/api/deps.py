from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import AdminUser, User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def require_role(*roles: str):
    def dependency() -> tuple[str, ...]:
        return roles

    return dependency


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    unauthorized = _unauthorized()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        admin_id = int(payload.get("sub", ""))
    except (TypeError, ValueError):
        raise unauthorized from None

    result = db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise unauthorized
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin user")
    if admin.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return admin


def require_admin(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    return admin


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = _unauthorized()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.startswith("user:"):
            raise ValueError("Unified user token subject required")
        user_id = int(subject.removeprefix("user:"))
    except (TypeError, ValueError):
        raise unauthorized from None

    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise unauthorized
    return user


def require_user_role(*roles: UserRole) -> Callable[[User], User]:
    allowed_roles = tuple(role.value for role in roles)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role required")
        return user

    return dependency


require_partner = require_user_role(UserRole.PARTNER)
require_client = require_user_role(UserRole.CLIENT)
require_unified_admin = require_user_role(UserRole.ADMIN)
