from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all SQLAlchemy models for test metadata
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.city import City
from app.models.client import ClientProfile
from app.models.partner import Partner, PartnerOffer
from app.models.payment import Subscription, SubscriptionStatus
from app.models.user import AdminUser, User, UserRole
from app.models.verification import PrivilegeVerificationSession, PrivilegeVerificationStatus


@pytest.fixture()
def verification_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with session_factory() as session:
        admin = AdminUser(
            email="admin@example.com",
            password_hash=hash_password("AdminPassword123"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        client_user = User(
            email="client@example.com",
            phone="+79990000001",
            password_hash=hash_password("ClientPassword123"),
            role=UserRole.CLIENT.value,
            is_active=True,
        )
        other_client_user = User(
            email="other-client@example.com",
            phone="+79990000002",
            password_hash=hash_password("OtherClientPassword123"),
            role=UserRole.CLIENT.value,
            is_active=True,
        )
        partner_user = User(
            email="partner@example.com",
            phone="+79990000003",
            password_hash=hash_password("PartnerPassword123"),
            role=UserRole.PARTNER.value,
            is_active=True,
        )
        other_partner_user = User(
            email="other-partner@example.com",
            phone="+79990000004",
            password_hash=hash_password("OtherPartnerPassword123"),
            role=UserRole.PARTNER.value,
            is_active=True,
        )
        session.add_all([admin, client_user, other_client_user, partner_user, other_partner_user])
        session.flush()

        city = City(name="Москва", slug="moscow", is_active=True, sort_order=10)
        other_city = City(name="Санкт-Петербург", slug="spb", is_active=True, sort_order=20)
        session.add_all([city, other_city])
        session.flush()

        client_profile = ClientProfile(
            user_id=client_user.id,
            full_name="Client One",
            source="seed",
            is_active=True,
        )
        other_client_profile = ClientProfile(
            user_id=other_client_user.id,
            full_name="Client Two",
            source="seed",
            is_active=True,
        )
        session.add_all([client_profile, other_client_profile])
        session.flush()

        partner = Partner(
            city_id=city.id,
            owner_user_id=partner_user.id,
            category_slug="beauty",
            name="Alpha Beauty",
            is_active=True,
            is_verified=True,
            sort_order=10,
        )
        other_partner = Partner(
            city_id=other_city.id,
            owner_user_id=other_partner_user.id,
            category_slug="fitness",
            name="Beta Yoga",
            is_active=True,
            is_verified=False,
            sort_order=20,
        )
        inactive_partner = Partner(
            city_id=city.id,
            name="Hidden Partner",
            is_active=False,
            is_verified=False,
            sort_order=30,
        )
        session.add_all([partner, other_partner, inactive_partner])
        session.flush()

        offer = PartnerOffer(partner_id=partner.id, title="Active Discount", is_active=True, sort_order=10)
        inactive_offer = PartnerOffer(partner_id=partner.id, title="Inactive Discount", is_active=False, sort_order=20)
        other_offer = PartnerOffer(partner_id=other_partner.id, title="Other Discount", is_active=True, sort_order=10)
        session.add_all([offer, inactive_offer, other_offer])
        session.flush()

        now = datetime.now(timezone.utc)
        session.add(
            Subscription(
                client_id=client_profile.id,
                status=SubscriptionStatus.active.value,
                starts_at=now - timedelta(days=1),
                ends_at=now + timedelta(days=30),
            )
        )
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            client.session_factory = session_factory  # type: ignore[attr-defined]
            yield client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user_login(client: TestClient, login: str, password: str) -> str:
    response = client.post("/api/v1/auth/user-login", json={"login": login, "password": password})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _admin_token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "AdminPassword123"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _client_token(client: TestClient) -> str:
    return _user_login(client, "client@example.com", "ClientPassword123")


def _other_client_token(client: TestClient) -> str:
    return _user_login(client, "other-client@example.com", "OtherClientPassword123")


def _partner_token(client: TestClient) -> str:
    return _user_login(client, "partner@example.com", "PartnerPassword123")


def _other_partner_token(client: TestClient) -> str:
    return _user_login(client, "other-partner@example.com", "OtherPartnerPassword123")


def _session(client: TestClient) -> Session:
    return client.session_factory()  # type: ignore[attr-defined,no-any-return]


def _create_verification(
    client: TestClient,
    *,
    client_id: int = 1,
    partner_id: int = 1,
    offer_id: int | None = None,
    status: str = PrivilegeVerificationStatus.active.value,
    expires_delta: timedelta = timedelta(minutes=5),
) -> int:
    now = datetime.now(timezone.utc)
    with _session(client) as session:
        verification = PrivilegeVerificationSession(
            client_id=client_id,
            partner_id=partner_id,
            offer_id=offer_id,
            code="123456",
            status=status,
            source="test",
            expires_at=now + expires_delta,
            confirmed_at=now if status == PrivilegeVerificationStatus.confirmed.value else None,
            created_at=now,
        )
        session.add(verification)
        session.commit()
        return verification.id


def test_client_post_verify_without_token_returns_401(verification_client: TestClient) -> None:
    response = verification_client.post("/api/v1/clients/partners/1/verify", json={})

    assert response.status_code == 401


def test_client_post_verify_with_partner_token_returns_403(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={},
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 403


def test_client_post_verify_creates_active_session_for_active_partner(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"source": "web"},
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == 1
    assert data["partner_id"] == 1
    assert data["partner_name"] == "Alpha Beauty"
    assert data["offer_id"] is None
    assert data["status"] == "active"
    assert data["source"] == "web"
    assert data["subscription_required"] is False
    assert len(data["code"]) == 6
    assert data["code"].isdigit()
    assert 0 < data["ttl_seconds"] <= 300


def test_client_post_verify_with_inactive_or_missing_partner_returns_404(verification_client: TestClient) -> None:
    token = _client_token(verification_client)

    inactive_response = verification_client.post(
        "/api/v1/clients/partners/3/verify",
        json={},
        headers=_auth_headers(token),
    )
    missing_response = verification_client.post(
        "/api/v1/clients/partners/999/verify",
        json={},
        headers=_auth_headers(token),
    )

    assert inactive_response.status_code == 404
    assert inactive_response.json()["detail"] == "Partner not found"
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Partner not found"


def test_client_post_verify_with_active_offer_creates_session_with_offer_info(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 1},
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["offer_id"] == 1
    assert data["offer_title"] == "Active Discount"


def test_client_post_verify_with_inactive_offer_returns_404(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 2},
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Offer not found"


def test_client_post_verify_with_offer_from_another_partner_returns_404(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 3},
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Offer not found"


def test_client_post_verify_without_active_subscription_returns_400(verification_client: TestClient) -> None:
    response = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 1},
        headers=_auth_headers(_other_client_token(verification_client)),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Active subscription required"


def test_client_post_verify_reuses_existing_active_session(verification_client: TestClient) -> None:
    token = _auth_headers(_client_token(verification_client))
    first = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 1},
        headers=token,
    )
    second = verification_client.post(
        "/api/v1/clients/partners/1/verify",
        json={"offer_id": 1},
        headers=token,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["code"] == first.json()["code"]


def test_client_get_own_verifications_returns_only_own_sessions(verification_client: TestClient) -> None:
    own_id = _create_verification(verification_client, client_id=1, partner_id=1)
    _create_verification(verification_client, client_id=2, partner_id=1)

    response = verification_client.get(
        "/api/v1/clients/me/verifications",
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [own_id]


def test_client_get_own_verifications_supports_status_filter(verification_client: TestClient) -> None:
    _create_verification(verification_client, client_id=1, partner_id=1, status="active")
    confirmed_id = _create_verification(verification_client, client_id=1, partner_id=1, status="confirmed")

    response = verification_client.get(
        "/api/v1/clients/me/verifications?status=confirmed",
        headers=_auth_headers(_client_token(verification_client)),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [confirmed_id]


def test_partner_get_own_verifications_returns_only_own_partner_sessions(verification_client: TestClient) -> None:
    own_id = _create_verification(verification_client, client_id=1, partner_id=1)
    _create_verification(verification_client, client_id=1, partner_id=2)

    response = verification_client.get(
        "/api/v1/partners/me/verifications",
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [own_id]
    assert data[0]["client_name"] == "Client One"


def test_partner_confirm_own_active_session_succeeds_and_sets_confirmed_at(verification_client: TestClient) -> None:
    verification_id = _create_verification(verification_client, client_id=1, partner_id=1)

    response = verification_client.post(
        f"/api/v1/partners/me/verifications/{verification_id}/confirm",
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == verification_id
    assert data["status"] == "confirmed"
    assert data["confirmed_at"] is not None
    with _session(verification_client) as session:
        stored = session.get(PrivilegeVerificationSession, verification_id)
        assert stored is not None
        assert stored.status == "confirmed"
        assert stored.confirmed_at is not None


def test_partner_confirm_another_partner_session_returns_404(verification_client: TestClient) -> None:
    verification_id = _create_verification(verification_client, client_id=1, partner_id=2)

    response = verification_client.post(
        f"/api/v1/partners/me/verifications/{verification_id}/confirm",
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Verification session not found"


def test_partner_confirm_expired_active_session_sets_expired_and_returns_400(verification_client: TestClient) -> None:
    verification_id = _create_verification(
        verification_client,
        client_id=1,
        partner_id=1,
        expires_delta=timedelta(minutes=-1),
    )

    response = verification_client.post(
        f"/api/v1/partners/me/verifications/{verification_id}/confirm",
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification session expired"
    with _session(verification_client) as session:
        stored = session.get(PrivilegeVerificationSession, verification_id)
        assert stored is not None
        assert stored.status == "expired"


def test_partner_confirm_non_active_session_returns_400(verification_client: TestClient) -> None:
    verification_id = _create_verification(
        verification_client,
        client_id=1,
        partner_id=1,
        status=PrivilegeVerificationStatus.confirmed.value,
    )

    response = verification_client.post(
        f"/api/v1/partners/me/verifications/{verification_id}/confirm",
        headers=_auth_headers(_partner_token(verification_client)),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification session is not active"


def test_admin_get_verifications_returns_all_sessions(verification_client: TestClient) -> None:
    first_id = _create_verification(verification_client, client_id=1, partner_id=1, offer_id=1)
    second_id = _create_verification(verification_client, client_id=2, partner_id=2)

    response = verification_client.get(
        "/api/v1/admin/verifications",
        headers=_auth_headers(_admin_token(verification_client)),
    )

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == [second_id, first_id]
    assert data[1]["partner_name"] == "Alpha Beauty"
    assert data[1]["city_name"] == "Москва"
    assert data[1]["offer_title"] == "Active Discount"


def test_admin_get_verifications_filters_by_partner_client_and_status(verification_client: TestClient) -> None:
    matching_id = _create_verification(
        verification_client,
        client_id=1,
        partner_id=1,
        status=PrivilegeVerificationStatus.confirmed.value,
    )
    _create_verification(verification_client, client_id=2, partner_id=1, status="confirmed")
    _create_verification(verification_client, client_id=1, partner_id=2, status="confirmed")
    _create_verification(verification_client, client_id=1, partner_id=1, status="active")

    response = verification_client.get(
        "/api/v1/admin/verifications?partner_id=1&client_id=1&status=confirmed",
        headers=_auth_headers(_admin_token(verification_client)),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [matching_id]


def test_tokens_with_wrong_roles_are_rejected_on_relevant_endpoints(verification_client: TestClient) -> None:
    client_token = _client_token(verification_client)
    partner_token = _partner_token(verification_client)
    admin_token = _admin_token(verification_client)

    partner_response = verification_client.get(
        "/api/v1/partners/me/verifications",
        headers=_auth_headers(client_token),
    )
    admin_response = verification_client.get(
        "/api/v1/admin/verifications",
        headers=_auth_headers(client_token),
    )
    client_response = verification_client.get(
        "/api/v1/clients/me/verifications",
        headers=_auth_headers(partner_token),
    )
    admin_on_client_response = verification_client.get(
        "/api/v1/clients/me/verifications",
        headers=_auth_headers(admin_token),
    )
    client_on_admin_response = verification_client.get(
        "/api/v1/admin/verifications",
        headers=_auth_headers(partner_token),
    )

    assert partner_response.status_code == 403
    assert admin_response.status_code == 401
    assert client_response.status_code == 403
    assert admin_on_client_response.status_code == 401
    assert client_on_admin_response.status_code == 401


def test_other_client_cannot_see_first_client_verifications(verification_client: TestClient) -> None:
    _create_verification(verification_client, client_id=1, partner_id=1)

    response = verification_client.get(
        "/api/v1/clients/me/verifications",
        headers=_auth_headers(_other_client_token(verification_client)),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_other_partner_can_confirm_only_own_session(verification_client: TestClient) -> None:
    own_id = _create_verification(verification_client, client_id=1, partner_id=2)

    response = verification_client.post(
        f"/api/v1/partners/me/verifications/{own_id}/confirm",
        headers=_auth_headers(_other_partner_token(verification_client)),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
