from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VkLinkCodeStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    selected_city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vk_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="client_profile")
    selected_city: Mapped["City | None"] = relationship("City", back_populates="client_profiles")
    payment_requests: Mapped[list["PaymentRequest"]] = relationship("PaymentRequest", back_populates="client")
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="client")
    verification_sessions: Mapped[list["PrivilegeVerificationSession"]] = relationship(
        "PrivilegeVerificationSession",
        back_populates="client",
    )
    vk_link_codes: Mapped[list["VkLinkCode"]] = relationship("VkLinkCode", back_populates="client")


class VkLinkCode(Base):
    __tablename__ = "vk_link_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=VkLinkCodeStatus.ACTIVE.value)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    client: Mapped["ClientProfile"] = relationship("ClientProfile", back_populates="vk_link_codes")
