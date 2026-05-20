from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel
from pydantic import model_validator



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


class VkMiniAppLoginRequest(BaseModel):
    launch_params: str | None = None
    params: dict[str, str] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "VkMiniAppLoginRequest":
        if not self.launch_params and not self.params:
            raise ValueError("Either launch_params or params must be provided")
        return self


class VkMiniAppLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UnifiedUserRead
    client: "VkMiniAppClientRead"


class VkMiniAppClientRead(BaseModel):
    id: int
    user_id: int
    vk_user_id: str | None
    full_name: str | None
    selected_city_id: int | None
    source: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class PasswordSetupCompleteRequest(BaseModel):
    token: str
    password: str
    password_confirm: str | None = None


class PasswordSetupCompleteResponse(BaseModel):
    ok: bool
    login: str | None = None
    message: str | None = None
