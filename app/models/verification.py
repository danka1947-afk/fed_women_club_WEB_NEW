from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PrivilegeVerificationStatus(str, Enum):
    active = "active"
    confirmed = "confirmed"
    expired = "expired"
    cancelled = "cancelled"


class PrivilegeVerificationSession(Base):
    __tablename__ = "privilege_verification_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"), nullable=False, index=True)
    offer_id: Mapped[int | None] = mapped_column(ForeignKey("partner_offers.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=PrivilegeVerificationStatus.active.value)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    client: Mapped["ClientProfile"] = relationship("ClientProfile", back_populates="verification_sessions")
    partner: Mapped["Partner"] = relationship("Partner", back_populates="verification_sessions")
    offer: Mapped["PartnerOffer | None"] = relationship("PartnerOffer", back_populates="verification_sessions")
