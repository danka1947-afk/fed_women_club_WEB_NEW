from __future__ import annotations

from collections.abc import Generator

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
from app.models.city import City
from app.models.partner import Partner
from app.models.user import AdminUser, User, UserRole


@pytest.fixture()
def admin_client() -> Generator[TestClient, None, None]:
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
        city_one = City(name="Москва", slug="moscow", is_active=True, sort_order=10)
        city_two = City(name="Санкт-Петербург", slug="spb", is_active=True, sort_order=20)
        partner_owner = User(email="owner@example.com", role=UserRole.PARTNER.value, is_active=True)
        client_owner = User(email="client@example.com", role=UserRole.CLIENT.value, is_active=True)
        session.add_all([city_one, city_two, partner_owner, client_owner])
        session.flush()
        session.add_all(
            [
                Partner(
                    city_id=city_one.id,
                    owner_user_id=partner_owner.id,
                    category_slug="krasota",
                    name="Alpha Beauty",
                    is_active=True,
                    is_verified=True,
                    sort_order=20,
                ),
                Partner(
                    city_id=city_two.id,
                    category_slug="fitnes-yoga",
                    name="Beta Yoga",
                    is_active=False,
                    sort_order=10,
                ),
            ]
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


@pytest.fixture()
def admin_token(admin_client: TestClient) -> str:
    response = admin_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _partner_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "city_id": 1,
        "category_slug": "krasota",
        "name": "Новый партнер",
        "description": "Описание",
        "address": "Адрес",
        "phone": "+79990000000",
        "website_url": "https://example.com",
        "social_url": "https://social.example.com",
        "working_hours": "10:00-20:00",
        "logo_url": "https://example.com/logo.png",
        "cover_url": "https://example.com/cover.png",
        "is_active": True,
        "is_verified": False,
        "sort_order": 5,
    }
    payload.update(overrides)
    return payload


def test_admin_partners_returns_401_without_token(admin_client: TestClient) -> None:
    response = admin_client.get("/api/v1/admin/partners")

    assert response.status_code == 401


def test_admin_partners_returns_list_ordered_with_admin_token(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [partner["name"] for partner in data] == ["Beta Yoga", "Alpha Beauty"]
    assert [partner["sort_order"] for partner in data] == [10, 20]
    assert data[0]["city_name"] == "Санкт-Петербург"
    assert data[1]["owner_email"] == "owner@example.com"


def test_admin_partner_create_with_valid_city(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(name="  Новый партнер  ", description="  Описание  "),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["city_id"] == 1
    assert data["name"] == "Новый партнер"
    assert data["description"] == "Описание"
    assert data["city_name"] == "Москва"


def test_admin_partner_create_missing_city_returns_404(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(city_id=9999),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "City not found"


def test_admin_partner_create_empty_name_returns_400(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(name="   "),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Partner name must not be empty"


def test_admin_partner_create_non_partner_owner_returns_400(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(owner_user_id=2),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Owner user must have partner role"


def test_admin_partner_create_partner_owner_succeeds_with_owner_email(
    admin_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(owner_user_id=1),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["owner_user_id"] == 1
    assert data["owner_email"] == "owner@example.com"


def test_admin_partner_create_unknown_category_returns_400(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.post(
        "/api/v1/admin/partners",
        headers=_auth_headers(admin_token),
        json=_partner_payload(category_slug="unknown-category"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown category slug"


def test_admin_partner_get_returns_partner_with_city_name(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners/1", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alpha Beauty"
    assert data["city_name"] == "Москва"


def test_admin_partner_get_missing_returns_404(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners/9999", headers=_auth_headers(admin_token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Partner not found"


def test_admin_partner_patch_updates_fields(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.patch(
        "/api/v1/admin/partners/1",
        headers=_auth_headers(admin_token),
        json={
            "city_id": 2,
            "category_slug": "fitnes-yoga",
            "name": "  Updated Partner  ",
            "is_active": False,
            "sort_order": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["city_id"] == 2
    assert data["city_name"] == "Санкт-Петербург"
    assert data["category_slug"] == "fitnes-yoga"
    assert data["name"] == "Updated Partner"
    assert data["is_active"] is False
    assert data["sort_order"] == 1


def test_admin_partner_patch_can_clear_owner_user_id(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.patch(
        "/api/v1/admin/partners/1",
        headers=_auth_headers(admin_token),
        json={"owner_user_id": None},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["owner_user_id"] is None
    assert data["owner_email"] is None


def test_admin_partners_list_supports_city_id_filter(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners?city_id=1", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [partner["name"] for partner in data] == ["Alpha Beauty"]


def test_admin_partners_list_supports_is_active_filter(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners?is_active=false", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [partner["name"] for partner in data] == ["Beta Yoga"]


def test_admin_partners_list_supports_category_slug_filter(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get(
        "/api/v1/admin/partners?category_slug=fitnes-yoga",
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert [partner["name"] for partner in data] == ["Beta Yoga"]


def test_admin_partners_list_supports_q_search(admin_client: TestClient, admin_token: str) -> None:
    response = admin_client.get("/api/v1/admin/partners?q=beaut", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [partner["name"] for partner in data] == ["Alpha Beauty"]
