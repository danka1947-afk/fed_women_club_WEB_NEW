from __future__ import annotations

from typing import Any, TypedDict

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
