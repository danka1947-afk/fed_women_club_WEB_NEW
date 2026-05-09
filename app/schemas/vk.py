from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.auth import UnifiedUserRead


class VkLinkCodeRead(BaseModel):
    code: str
    status: str
    expires_at: datetime
    ttl_seconds: int


class VkExchangeLinkCodeRequest(BaseModel):
    vk_user_id: str
    code: str


class VkTokenRequest(BaseModel):
    vk_user_id: str


class VkExchangeTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UnifiedUserRead
