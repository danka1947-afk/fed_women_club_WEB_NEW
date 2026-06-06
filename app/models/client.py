from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
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
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    custom_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vk_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    telegram_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telegram_photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trial_subscription_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
    identity_links: Mapped[list["ClientIdentityLink"]] = relationship(
        "ClientIdentityLink",
        back_populates="client_profile",
        cascade="all, delete-orphan",
    )


class ClientIdentityLink(Base):
    __tablename__ = "client_identity_links"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_client_identity_links_provider_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_profile_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    client_profile: Mapped["ClientProfile"] = relationship("ClientProfile", back_populates="identity_links")


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


class ClientPasswordSetupToken(Base):
    __tablename__ = "client_password_setup_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    purpose: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="vk_onboarding_password_setup",
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    source: Mapped[str | None] = mapped_column(String(64), nullable=True, default="vk")
    vk_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="password_setup_tokens")
