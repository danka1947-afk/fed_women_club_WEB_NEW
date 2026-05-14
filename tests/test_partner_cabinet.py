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
from app.models.partner import Partner, PartnerOffer
from app.models.user import AdminUser, User, UserRole


@pytest.fixture()
def partner_client() -> Generator[TestClient, None, None]:
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
                password_hash=hash_password("AdminPassword123"),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
        )
        partner_owner = User(
            email="partner@example.com",
            phone="+79990000001",
            password_hash=hash_password("PartnerPassword123"),
            role=UserRole.PARTNER.value,
            is_active=True,
        )
        other_partner_owner = User(
            email="other-partner@example.com",
            phone="+79990000002",
            password_hash=hash_password("OtherPartnerPassword123"),
            role=UserRole.PARTNER.value,
            is_active=True,
        )
        unbound_partner = User(
            email="unbound@example.com",
            phone="+79990000003",
            password_hash=hash_password("UnboundPassword123"),
            role=UserRole.PARTNER.value,
            is_active=True,
        )
        client_user = User(
            email="client@example.com",
            phone="+79990000004",
            password_hash=hash_password("ClientPassword123"),
            role=UserRole.CLIENT.value,
            is_active=True,
        )
        city = City(name="Москва", slug="moscow", is_active=True, sort_order=10)
        other_city = City(name="Санкт-Петербург", slug="spb", is_active=True, sort_order=20)
        session.add_all([partner_owner, other_partner_owner, unbound_partner, client_user, city, other_city])
        session.flush()

        partner = Partner(
            city_id=city.id,
            owner_user_id=partner_owner.id,
            category_slug="krasota",
            name="Alpha Beauty",
            description="Initial description",
            address="Initial address",
            phone="+70000000001",
            website_url="https://alpha.example.com",
            social_url="https://social.example.com/alpha",
            working_hours="10:00-20:00",
            logo_url="https://alpha.example.com/logo.png",
            cover_url="https://alpha.example.com/cover.png",
            is_active=True,
            is_verified=True,
            sort_order=20,
        )
        other_partner = Partner(
            city_id=other_city.id,
            owner_user_id=other_partner_owner.id,
            category_slug="fitnes-yoga",
            name="Beta Yoga",
            is_active=True,
            is_verified=False,
            sort_order=10,
        )
        session.add_all([partner, other_partner])
        session.flush()

        session.add_all(
            [
                PartnerOffer(
                    partner_id=partner.id,
                    title="Later offer",
                    benefit_text="Later benefit",
                    is_active=True,
                    sort_order=20,
                ),
                PartnerOffer(
                    partner_id=partner.id,
                    title="First same sort",
                    is_active=True,
                    sort_order=10,
                ),
                PartnerOffer(
                    partner_id=partner.id,
                    title="Second same sort inactive",
                    is_active=False,
                    sort_order=10,
                ),
                PartnerOffer(
                    partner_id=other_partner.id,
                    title="Other partner offer",
                    is_active=True,
                    sort_order=1,
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
def admin_token(partner_client: TestClient) -> str:
    response = partner_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "AdminPassword123"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user_login(client: TestClient, login: str, password: str) -> str:
    response = client.post("/api/v1/auth/user-login", json={"login": login, "password": password})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _partner_token(client: TestClient) -> str:
    return _user_login(client, "partner@example.com", "PartnerPassword123")


def _client_token(client: TestClient) -> str:
    return _user_login(client, "client@example.com", "ClientPassword123")


def _unbound_partner_token(client: TestClient) -> str:
    return _user_login(client, "unbound@example.com", "UnboundPassword123")


def _offer_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "  Скидка на уход  ",
        "description": "  Подробное описание  ",
        "benefit_text": "  -15% для клуба  ",
        "conditions": "  По записи  ",
        "base_price": "1000.00",
        "discount_percent": "15.50",
        "image_url": "  https://example.com/offer.png  ",
        "is_active": True,
        "sort_order": 5,
    }
    payload.update(overrides)
    return payload


def test_partner_me_returns_401_without_token(partner_client: TestClient) -> None:
    response = partner_client.get("/api/v1/partners/me")

    assert response.status_code == 401


def test_partner_me_rejects_admin_user_token(partner_client: TestClient, admin_token: str) -> None:
    response = partner_client.get("/api/v1/partners/me", headers=_auth_headers(admin_token))

    assert response.status_code == 401


def test_partner_me_rejects_client_unified_token(partner_client: TestClient) -> None:
    token = _client_token(partner_client)

    response = partner_client.get("/api/v1/partners/me", headers=_auth_headers(token))

    assert response.status_code == 403


def test_partner_me_with_unbound_partner_returns_404(partner_client: TestClient) -> None:
    token = _unbound_partner_token(partner_client)

    response = partner_client.get("/api/v1/partners/me", headers=_auth_headers(token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Partner profile for current user was not found"


def test_partner_me_returns_bound_profile_with_city_name(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.get("/api/v1/partners/me", headers=_auth_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["city_id"] == 1
    assert data["city_name"] == "Москва"
    assert data["owner_user_id"] == 1
    assert data["category_slug"] == "krasota"
    assert data["name"] == "Alpha Beauty"
    assert data["is_active"] is True
    assert data["is_verified"] is True


def test_partner_me_patch_updates_public_fields_and_strips_empty_to_null(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.patch(
        "/api/v1/partners/me",
        headers=_auth_headers(token),
        json={
            "description": "  Updated description  ",
            "address": "   ",
            "phone": "  +79991234567  ",
            "website_url": "",
            "social_url": "  https://social.example.com/new  ",
            "working_hours": "  11:00-19:00  ",
            "logo_url": "   ",
            "cover_url": "  https://example.com/new-cover.png  ",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["address"] is None
    assert data["phone"] == "+79991234567"
    assert data["website_url"] is None
    assert data["social_url"] == "https://social.example.com/new"
    assert data["working_hours"] == "11:00-19:00"
    assert data["logo_url"] is None
    assert data["cover_url"] == "https://example.com/new-cover.png"


def test_partner_me_patch_ignores_protected_fields(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.patch(
        "/api/v1/partners/me",
        headers=_auth_headers(token),
        json={
            "city_id": 2,
            "owner_user_id": 2,
            "category_slug": "fitnes-yoga",
            "name": "Changed Name",
            "is_active": False,
            "is_verified": False,
            "sort_order": 999,
            "description": "Allowed update",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Allowed update"
    assert data["city_id"] == 1
    assert data["owner_user_id"] == 1
    assert data["category_slug"] == "krasota"
    assert data["name"] == "Alpha Beauty"
    assert data["is_active"] is True
    assert data["is_verified"] is True


def test_partner_offers_returns_only_own_offers_ordered(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.get("/api/v1/partners/me/offers", headers=_auth_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert [offer["title"] for offer in data] == [
        "First same sort",
        "Second same sort inactive",
        "Later offer",
    ]
    assert [offer["sort_order"] for offer in data] == [10, 10, 20]
    assert {offer["partner_id"] for offer in data} == {1}


def test_partner_offers_supports_is_active_filter(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.get(
        "/api/v1/partners/me/offers?is_active=false",
        headers=_auth_headers(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert [offer["title"] for offer in data] == ["Second same sort inactive"]
    assert data[0]["is_active"] is False


def test_partner_offer_create_under_own_partner(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/offers",
        headers=_auth_headers(token),
        json=_offer_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["partner_id"] == 1
    assert data["title"] == "Скидка на уход"
    assert data["description"] == "Подробное описание"
    assert data["benefit_text"] == "-15% для клуба"
    assert data["conditions"] == "По записи"
    assert data["base_price"] in ("1000.00", 1000.0)
    assert data["discount_percent"] in ("15.50", 15.5)
    assert data["image_url"] == "https://example.com/offer.png"
    assert data["is_active"] is True
    assert data["sort_order"] == 5


def test_partner_offer_create_empty_title_returns_400(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/offers",
        headers=_auth_headers(token),
        json=_offer_payload(title="   "),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Offer title must not be empty"


@pytest.mark.parametrize(
    ("field", "value", "detail"),
    [
        ("base_price", "-0.01", "base_price must be greater than or equal to 0"),
        ("discount_percent", "-0.01", "discount_percent must be between 0 and 100"),
        ("discount_percent", "100.01", "discount_percent must be between 0 and 100"),
    ],
)
def test_partner_offer_create_invalid_amounts_return_400(
    partner_client: TestClient,
    field: str,
    value: str,
    detail: str,
) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/offers",
        headers=_auth_headers(token),
        json=_offer_payload(**{field: value}),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == detail


def test_partner_offer_patch_updates_own_offer(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.patch(
        "/api/v1/partners/me/offers/1",
        headers=_auth_headers(token),
        json={
            "title": "  Updated offer  ",
            "benefit_text": "  Updated benefit  ",
            "base_price": "1500.00",
            "discount_percent": "20.00",
            "is_active": False,
            "sort_order": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["partner_id"] == 1
    assert data["title"] == "Updated offer"
    assert data["benefit_text"] == "Updated benefit"
    assert data["base_price"] in ("1500.00", 1500.0)
    assert data["discount_percent"] in ("20.00", 20.0)
    assert data["is_active"] is False
    assert data["sort_order"] == 1


def test_partner_offer_patch_other_partner_offer_returns_404(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.patch(
        "/api/v1/partners/me/offers/4",
        headers=_auth_headers(token),
        json={"title": "Should not update"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Offer not found"


def test_partner_offer_patch_can_clear_optional_text_to_null(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.patch(
        "/api/v1/partners/me/offers/1",
        headers=_auth_headers(token),
        json={
            "description": "   ",
            "benefit_text": "",
            "conditions": None,
            "image_url": "  https://example.com/new.png  ",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] is None
    assert data["benefit_text"] is None
    assert data["conditions"] is None
    assert data["image_url"] == "https://example.com/new.png"

TINY_PROFILE_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00"
    b"\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_partner_uploads_own_logo_updates_own_profile(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/images?kind=logo",
        headers=_auth_headers(token),
        files={"file": ("logo.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["kind"] == "logo"
    assert data["url"].startswith("/uploads/partners/1/logo-")

    profile_response = partner_client.get("/api/v1/partners/me", headers=_auth_headers(token))
    assert profile_response.json()["logo_url"] == data["url"]


def test_partner_uploads_me_endpoint_does_not_update_another_partner(partner_client: TestClient, admin_token: str) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/images?kind=cover",
        headers=_auth_headers(token),
        files={"file": ("cover.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["url"].startswith("/uploads/partners/1/cover-")

    other_response = partner_client.get("/api/v1/admin/partners/2", headers=_auth_headers(admin_token))
    assert other_response.status_code == 200
    assert other_response.json()["cover_url"] is None


def test_partner_upload_rejects_unauthorized_request(partner_client: TestClient) -> None:
    response = partner_client.post(
        "/api/v1/partners/me/images?kind=logo",
        files={"file": ("logo.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 401


def test_partner_uploads_own_offer_image_updates_offer(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/offers/1/image",
        headers=_auth_headers(token),
        files={"file": ("ignored-original-name.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"url"}
    assert data["url"].startswith("/uploads/partners/1/offers/1/offer-")
    assert data["url"].endswith(".png")

    offers_response = partner_client.get("/api/v1/partners/me/offers", headers=_auth_headers(token))
    uploaded_offer = next(offer for offer in offers_response.json() if offer["id"] == 1)
    assert uploaded_offer["image_url"] == data["url"]


def test_partner_cannot_upload_another_partners_offer_image(partner_client: TestClient) -> None:
    token = _partner_token(partner_client)

    response = partner_client.post(
        "/api/v1/partners/me/offers/4/image",
        headers=_auth_headers(token),
        files={"file": ("offer.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 404


def test_partner_offer_upload_rejects_unauthorized_request(partner_client: TestClient) -> None:
    response = partner_client.post(
        "/api/v1/partners/me/offers/1/image",
        files={"file": ("offer.png", TINY_PROFILE_PNG_BYTES, "image/png")},
    )

    assert response.status_code == 401
