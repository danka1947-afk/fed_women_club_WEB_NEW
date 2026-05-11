from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel


class AuthPayload(TypedDict, total=False):
    data: dict[str, Any]


class LoginRequest(BaseModel):
    email: str
    password: str


class AdminUserRead(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AdminUserRead


class UserLoginRequest(BaseModel):
    login: str
    password: str


class UnifiedUserRead(BaseModel):
    id: int
    email: str | None
    phone: str | None
    role: Literal["admin", "partner", "client"]

    model_config = {"from_attributes": True}


class UnifiedTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UnifiedUserRead


class PasswordSetupCompleteRequest(BaseModel):
    token: str
    password: str
    password_confirm: str | None = None


class PasswordSetupCompleteResponse(BaseModel):
    ok: bool
    login: str | None = None
    message: str | None = None
