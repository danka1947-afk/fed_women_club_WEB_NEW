from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_admin
from app.models.user import AdminUser
from app.schemas.auth import AdminUserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=AdminUserRead)
def read_admin_me(admin: AdminUser = Depends(require_admin)) -> AdminUser:
    return admin
