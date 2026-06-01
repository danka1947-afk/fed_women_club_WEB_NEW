from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.landing import DEFAULT_GIVEAWAY_ITEMS, LandingSettings
from app.models.user import User, UserRole
from app.schemas.landing import GiveawayItem, PublicLandingStatsRead

LANDING_SETTINGS_ID = 1
CLIENT_MEMBER_ROLES = (UserRole.CLIENT.value, "member", "customer")


def normalize_giveaway_items(items: list[dict] | None) -> list[dict]:
    normalized: list[dict] = []
    source = items if isinstance(items, list) else []
    for index, item in enumerate(source):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        normalized.append(
            {
                "title": title,
                "description": str(item.get("description") or "").strip() or None,
                "is_active": bool(item.get("is_active", True)),
                "sort_order": int(item.get("sort_order") or index),
            }
        )
    return normalized or [item.copy() for item in DEFAULT_GIVEAWAY_ITEMS]


def get_or_create_landing_settings(db: Session) -> LandingSettings:
    settings = db.get(LandingSettings, LANDING_SETTINGS_ID)
    if settings is None:
        settings = LandingSettings(id=LANDING_SETTINGS_ID)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    if not settings.giveaway_items:
        settings.giveaway_items = [item.copy() for item in DEFAULT_GIVEAWAY_ITEMS]
    return settings


def calculate_public_members_count(db: Session, settings: LandingSettings | None = None) -> int:
    landing_settings = settings or get_or_create_landing_settings(db)
    real_members_count = db.execute(
        select(func.count(User.id)).where(
            User.role.in_(CLIENT_MEMBER_ROLES),
            User.is_active.is_(True),
        )
    ).scalar_one()
    return int(landing_settings.members_count_base or 0) + int(real_members_count or 0)


def get_primary_giveaway_title(items: list[dict], fallback: str) -> str:
    active_items = [item for item in normalize_giveaway_items(items) if item.get("is_active", True)]
    active_items.sort(key=lambda item: (int(item.get("sort_order") or 0), str(item.get("title") or "")))
    return str(active_items[0].get("title") or fallback).strip() or fallback


def build_public_landing_stats(db: Session) -> PublicLandingStatsRead:
    settings = get_or_create_landing_settings(db)
    giveaway_items = normalize_giveaway_items(settings.giveaway_items)
    current = get_primary_giveaway_title(giveaway_items, settings.giveaway_current)
    return PublicLandingStatsRead(
        members_count=calculate_public_members_count(db, settings),
        partners_count=int(settings.partners_count_display or 0),
        savings_total=int(settings.savings_total or 0),
        giveaway_title=settings.giveaway_title or "Розыгрыш месяца",
        giveaway_current=current,
        giveaway_subtitle=settings.giveaway_subtitle or "доступно участницам клуба",
        giveaway_items=[GiveawayItem(**item) for item in giveaway_items],
    )
