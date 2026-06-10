from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.content_base import ContentBase
from app.db.content_session import get_content_db
from app.db.session import get_db
from app.main import app
from app.models.user import AdminUser, UserRole


@pytest.fixture()
def content_admin_client() -> Generator[tuple[TestClient, str], None, None]:
    main_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    content_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    main_session_factory = sessionmaker(
        bind=main_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    content_session_factory = sessionmaker(
        bind=content_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )

    Base.metadata.create_all(bind=main_engine)
    ContentBase.metadata.create_all(bind=content_engine)
    with main_session_factory() as session:
        admin = AdminUser(
            email="admin@example.com",
            password_hash=hash_password("StrongPassword123"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        admin_id = admin.id

    def override_get_db() -> Generator[Session, None, None]:
        with main_session_factory() as session:
            yield session

    def override_get_content_db() -> Generator[Session, None, None]:
        with content_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_content_db] = override_get_content_db
    try:
        with TestClient(app) as client:
            yield client, create_access_token(str(admin_id))
    finally:
        app.dependency_overrides.clear()
        main_engine.dispose()
        content_engine.dispose()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_content_admin_crud_bootstraps_content_database(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client
    headers = _auth_headers(token)

    assert (
        client.post(
            "/api/content/admin/cities", json={"name": "Москва", "slug": "moscow"}
        ).status_code
        == 401
    )

    city_response = client.post(
        "/api/content/admin/cities",
        headers=headers,
        json={"name": "Москва", "slug": "moscow"},
    )
    assert city_response.status_code == 201
    city_id = city_response.json()["id"]

    category_response = client.post(
        "/api/content/admin/categories",
        headers=headers,
        json={"name": "Красота", "slug": "beauty"},
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    partner_response = client.post(
        "/api/content/admin/partners",
        headers=headers,
        json={
            "city_id": city_id,
            "category_slug": "beauty",
            "category_ids": [category_id],
            "name": "Bloom Spa",
            "description": "Спа-партнёр клуба",
            "address": "Тверская, 1",
            "phone": "+79990000000",
        },
    )
    assert partner_response.status_code == 201
    partner = partner_response.json()
    partner_id = partner["id"]
    assert partner["category_ids"] == [category_id]

    offer_response = client.post(
        f"/api/content/admin/partners/{partner_id}/offers",
        headers=headers,
        json={"title": "Массаж", "benefit_text": "Скидка 20%", "base_price": "3000.00"},
    )
    assert offer_response.status_code == 201
    offer_id = offer_response.json()["id"]

    partner_photo_response = client.post(
        f"/api/content/admin/partners/{partner_id}/photos",
        headers=headers,
        json={"url": "https://example.com/partner.jpg", "alt_text": "Интерьер"},
    )
    assert partner_photo_response.status_code == 201

    offer_photo_response = client.post(
        f"/api/content/admin/offers/{offer_id}/photos",
        headers=headers,
        json={"url": "https://example.com/offer.jpg", "alt_text": "Услуга"},
    )
    assert offer_photo_response.status_code == 201

    giveaway_response = client.post(
        "/api/content/admin/giveaways",
        headers=headers,
        json={"title": "Первый розыгрыш", "current": "Сертификат"},
    )
    assert giveaway_response.status_code == 201

    banner_response = client.post(
        "/api/content/admin/banners",
        headers=headers,
        json={
            "title": "Добро пожаловать",
            "image_url": "https://example.com/banner.jpg",
        },
    )
    assert banner_response.status_code == 201

    assert (
        client.patch(
            f"/api/content/admin/cities/{city_id}",
            headers=headers,
            json={"sort_order": 10},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/content/admin/categories/{category_id}",
            headers=headers,
            json={"sort_order": 20},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/content/admin/partners/{partner_id}",
            headers=headers,
            json={"is_verified": True},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/content/admin/offers/{offer_id}",
            headers=headers,
            json={"is_active": False},
        ).status_code
        == 200
    )

    assert (
        client.get("/api/content/admin/cities", headers=headers).json()[0]["name"]
        == "Москва"
    )
    assert (
        client.get(
            f"/api/content/admin/partners/{partner_id}/offers", headers=headers
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/content/admin/partners/{partner_id}/photos", headers=headers
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/content/admin/offers/{offer_id}/photos", headers=headers
        ).status_code
        == 200
    )
    assert (
        client.get("/api/content/admin/giveaways", headers=headers).status_code == 200
    )
    assert client.get("/api/content/admin/banners", headers=headers).status_code == 200


def test_public_content_endpoints_remain_read_only(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client

    create_response = client.post(
        "/api/content/cities",
        headers=_auth_headers(token),
        json={"name": "Москва", "slug": "moscow"},
    )

    assert create_response.status_code == 405


def test_public_content_blocks_returns_active_block(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client
    headers = _auth_headers(token)

    create_response = client.post(
        "/api/content/admin/blocks",
        headers=headers,
        json={
            "key": "home.hero.title",
            "placement": "static_texts",
            "locale": "ru",
            "title": "Hero title",
            "body": "Добро пожаловать",
            "metadata_json": {"editable": True},
            "is_active": True,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/content/blocks?type=static_texts")

    assert response.status_code == 200
    assert response.json() == [
        {
            "key": "home.hero.title",
            "placement": "static_texts",
            "locale": "ru",
            "title": "Hero title",
            "body": "Добро пожаловать",
            "metadata_json": {"editable": True},
            "is_active": True,
        }
    ]


def test_public_content_blocks_does_not_return_inactive_block(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client

    create_response = client.post(
        "/api/content/admin/blocks",
        headers=_auth_headers(token),
        json={
            "key": "home.hero.subtitle",
            "placement": "static_texts",
            "locale": "ru",
            "body": "Inactive text",
            "is_active": False,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/content/blocks?type=static_texts")

    assert response.status_code == 200
    assert response.json() == []


def test_admin_create_content_block_requires_admin_token(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, _token = content_admin_client

    response = client.post(
        "/api/content/admin/blocks",
        json={
            "key": "nav.home.label",
            "placement": "static_texts",
            "locale": "ru",
            "body": "Главная",
        },
    )

    assert response.status_code == 401


def test_admin_create_content_block_with_admin_token(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client

    response = client.post(
        "/api/content/admin/blocks",
        headers=_auth_headers(token),
        json={
            "key": "nav.home.label",
            "placement": "static_texts",
            "locale": "ru",
            "title": "Navigation home",
            "body": "Главная",
            "metadata_json": {"source": "telegram_admin_preview"},
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "key": "nav.home.label",
        "placement": "static_texts",
        "locale": "ru",
        "title": "Navigation home",
        "body": "Главная",
        "metadata_json": {"source": "telegram_admin_preview"},
        "is_active": True,
    }


def test_admin_update_content_block_updates_existing_block(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client
    headers = _auth_headers(token)

    create_response = client.post(
        "/api/content/admin/blocks",
        headers=headers,
        json={
            "key": "nav.partners.label",
            "placement": "static_texts",
            "locale": "ru",
            "body": "Партнёры",
            "is_active": True,
        },
    )
    assert create_response.status_code == 201

    response = client.patch(
        "/api/content/admin/blocks/nav.partners.label",
        headers=headers,
        json={"body": "Клуб", "metadata_json": {"updated": True}},
    )

    assert response.status_code == 200
    assert response.json()["key"] == "nav.partners.label"
    assert response.json()["locale"] == "ru"
    assert response.json()["body"] == "Клуб"
    assert response.json()["metadata_json"] == {"updated": True}


def test_admin_update_content_block_creates_missing_key(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client

    response = client.patch(
        "/api/content/admin/blocks/nav.privileges.label",
        headers=_auth_headers(token),
        json={"body": "Привилегии", "is_active": True},
    )

    assert response.status_code == 200
    assert response.json() == {
        "key": "nav.privileges.label",
        "placement": "static_texts",
        "locale": "ru",
        "title": None,
        "body": "Привилегии",
        "metadata_json": None,
        "is_active": True,
    }


def test_public_static_texts_returns_created_telegram_miniapp_blocks(
    content_admin_client: tuple[TestClient, str],
) -> None:
    client, token = content_admin_client
    headers = _auth_headers(token)
    expected_keys = [
        "nav.home.label",
        "nav.partners.label",
        "nav.privileges.label",
        "nav.savings.label",
        "nav.profile.label",
        "home.hero.title",
        "home.hero.subtitle",
    ]

    for key in expected_keys:
        response = client.patch(
            f"/api/content/admin/blocks/{key}",
            headers=headers,
            json={
                "placement": "static_texts",
                "locale": "ru",
                "body": f"Text for {key}",
                "is_active": True,
            },
        )
        assert response.status_code == 200

    response = client.get("/api/content/blocks?type=static_texts")

    assert response.status_code == 200
    blocks_by_key = {block["key"]: block for block in response.json()}
    assert sorted(blocks_by_key) == sorted(expected_keys)
    for key in expected_keys:
        assert blocks_by_key[key]["body"] == f"Text for {key}"
        assert blocks_by_key[key]["placement"] == "static_texts"
        assert blocks_by_key[key]["locale"] == "ru"
        assert blocks_by_key[key]["is_active"] is True
