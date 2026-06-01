from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all SQLAlchemy models for test metadata
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import AdminUser, User, UserRole


@pytest.fixture()
def landing_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    with session_factory() as session:
        session.add(
            AdminUser(
                email="admin@example.com",
                password_hash=hash_password("StrongPassword123"),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
        )
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_public_landing_stats_returns_start_values(landing_client: TestClient) -> None:
    response = landing_client.get("/api/v1/public/landing/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["members_count"] == 125
    assert data["partners_count"] == 18
    assert data["savings_total"] == 53500
    assert data["giveaway_title"] == "Розыгрыш месяца"


def test_public_members_count_grows_when_client_user_appears(landing_client: TestClient) -> None:
    with next(app.dependency_overrides[get_db]()) as session:
        session.add(User(email="client@example.com", role=UserRole.CLIENT.value, is_active=True))
        session.commit()

    response = landing_client.get("/api/v1/public/landing/stats")

    assert response.status_code == 200
    assert response.json()["members_count"] == 126


def test_admin_landing_settings_patch_saves_public_stats_and_giveaway(landing_client: TestClient) -> None:
    response = landing_client.patch(
        "/api/v1/admin/landing-settings",
        headers=_auth_headers(landing_client),
        json={
            "partners_count_display": 24,
            "savings_total": 75000,
            "giveaway_title": "Розыгрыш месяца",
            "giveaway_current": "Сертификат в SPA",
            "giveaway_subtitle": "для активных участниц",
            "giveaway_items": [
                {"title": "Сертификат в SPA", "description": "Главный приз", "is_active": True, "sort_order": 10},
                {"title": "Beauty box", "description": "Дополнительный приз", "is_active": True, "sort_order": 20},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["partners_count_display"] == 24
    assert data["savings_total"] == 75000
    assert data["giveaway_current"] == "Сертификат в SPA"
    assert [item["title"] for item in data["giveaway_items"]] == ["Сертификат в SPA", "Beauty box"]


def test_public_landing_stats_returns_updated_giveaway(landing_client: TestClient) -> None:
    headers = _auth_headers(landing_client)
    response = landing_client.patch(
        "/api/v1/admin/landing-settings",
        headers=headers,
        json={
            "giveaway_current": "Fallback prize",
            "giveaway_items": [
                {"title": "Неактивный приз", "is_active": False, "sort_order": 0},
                {"title": "Главный активный приз", "is_active": True, "sort_order": 1},
            ],
        },
    )
    assert response.status_code == 200

    public_response = landing_client.get("/api/v1/public/landing/stats")

    assert public_response.status_code == 200
    data = public_response.json()
    assert data["giveaway_current"] == "Главный активный приз"
    assert data["giveaway_items"][0]["title"] == "Неактивный приз"


def test_frontend_landing_hero_stats_do_not_use_legacy_hardcodes() -> None:
    text = Path("frontend/src/main.js").read_text(encoding="utf-8")

    assert "327" not in text
    assert "50+" not in text
    assert "183 000 ₽" not in text
    assert "Dyson" not in text
