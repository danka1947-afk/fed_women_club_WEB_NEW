from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import ast
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all SQLAlchemy models for test metadata
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.appointment import PartnerAppointment, PartnerAppointmentStatus
from app.models.city import City
from app.models.client import ClientProfile
from app.models.partner import Partner, PartnerOffer
from app.models.user import AdminUser, User, UserRole


@contextmanager
def _make_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    now = datetime.now(timezone.utc).replace(microsecond=0)

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
        no_phone_user = User(
            email="no-phone@example.com",
            phone=None,
            password_hash=hash_password("NoPhonePassword123"),
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
        unified_admin_user = User(
            email="unified-admin@example.com",
            phone="+79990000005",
            password_hash=hash_password("UnifiedAdminPassword123"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        session.add_all([
            admin,
            client_user,
            other_client_user,
            no_phone_user,
            partner_user,
            other_partner_user,
            unified_admin_user,
        ])
        session.flush()

        city = City(name="Москва", slug="moscow", is_active=True, sort_order=10)
        session.add(city)
        session.flush()

        client_profile = ClientProfile(user_id=client_user.id, full_name="Client One", is_active=True)
        other_client_profile = ClientProfile(user_id=other_client_user.id, full_name="Client Two", is_active=True)
        no_phone_profile = ClientProfile(user_id=no_phone_user.id, full_name="No Phone", is_active=True)
        session.add_all([client_profile, other_client_profile, no_phone_profile])
        session.flush()

        partner = Partner(
            city_id=city.id,
            owner_user_id=partner_user.id,
            category_slug="beauty",
            name="Alpha Beauty",
            is_active=True,
            is_verified=True,
        )
        other_partner = Partner(
            city_id=city.id,
            owner_user_id=other_partner_user.id,
            category_slug="fitness",
            name="Beta Yoga",
            is_active=True,
            is_verified=True,
        )
        inactive_partner = Partner(
            city_id=city.id,
            category_slug="beauty",
            name="Inactive Spa",
            is_active=False,
            is_verified=True,
        )
        session.add_all([partner, other_partner, inactive_partner])
        session.flush()

        offer = PartnerOffer(partner_id=partner.id, title="Alpha Offer", is_active=True)
        inactive_offer = PartnerOffer(partner_id=partner.id, title="Inactive Offer", is_active=False)
        other_offer = PartnerOffer(partner_id=other_partner.id, title="Beta Offer", is_active=True)
        session.add_all([offer, inactive_offer, other_offer])
        session.flush()

        session.add_all(
            [
                PartnerAppointment(
                    client_id=client_profile.id,
                    partner_id=partner.id,
                    offer_id=offer.id,
                    status=PartnerAppointmentStatus.CONFIRMED.value,
                    client_name="Client One",
                    client_phone="+79990000001",
                    source="seed",
                    created_at=now - timedelta(hours=2),
                    confirmed_at=now - timedelta(hours=1),
                ),
                PartnerAppointment(
                    client_id=other_client_profile.id,
                    partner_id=other_partner.id,
                    offer_id=other_offer.id,
                    status=PartnerAppointmentStatus.NEW.value,
                    client_name="Client Two",
                    client_phone="+79990000002",
                    source="seed",
                    created_at=now - timedelta(hours=3),
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


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user_login(client: TestClient, login: str, password: str) -> str:
    response = client.post("/api/v1/auth/user-login", json={"login": login, "password": password})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _admin_login(client: TestClient) -> str:
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "AdminPassword123"})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def test_client_create_auth_role_partner_offer_and_phone_validation() -> None:
    with _make_client() as client:
        assert client.post("/api/v1/clients/partners/1/appointments", json={}).status_code == 401
        partner_token = _user_login(client, "partner@example.com", "PartnerPassword123")
        admin_user_token = _user_login(client, "unified-admin@example.com", "UnifiedAdminPassword123")
        client_token = _user_login(client, "client@example.com", "ClientPassword123")
        no_phone_token = _user_login(client, "no-phone@example.com", "NoPhonePassword123")

        assert client.post(
            "/api/v1/clients/partners/1/appointments",
            json={},
            headers=_headers(partner_token),
        ).status_code == 403
        assert client.get("/api/v1/clients/me/appointments", headers=_headers(admin_user_token)).status_code == 403

        response = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"offer_id": 1, "client_name": "  Payload Name  ", "comment": "  hello  "},
            headers=_headers(client_token),
        )
        nullable_offer_response = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"client_phone": "+70000000000", "offer_id": None},
            headers=_headers(client_token),
        )
        missing_phone_response = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={},
            headers=_headers(no_phone_token),
        )
        other_offer_response = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"offer_id": 3},
            headers=_headers(client_token),
        )
        inactive_partner_response = client.post(
            "/api/v1/clients/partners/3/appointments",
            json={},
            headers=_headers(client_token),
        )
        inactive_offer_response = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"offer_id": 2},
            headers=_headers(client_token),
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "new"
    assert body["client_phone"] == "+79990000001"
    assert body["client_name"] == "Payload Name"
    assert body["client_email"] == "client@example.com"
    assert body["partner_name"] == "Alpha Beauty"
    assert body["offer_title"] == "Alpha Offer"
    assert nullable_offer_response.status_code == 201
    assert nullable_offer_response.json()["offer_id"] is None
    assert missing_phone_response.status_code == 400
    assert other_offer_response.status_code == 404
    assert inactive_partner_response.status_code == 404
    assert inactive_offer_response.status_code == 404


def test_client_list_only_own_appointments_and_status_filter() -> None:
    with _make_client() as client:
        token = _user_login(client, "client@example.com", "ClientPassword123")
        all_response = client.get("/api/v1/clients/me/appointments", headers=_headers(token))
        confirmed_response = client.get("/api/v1/clients/me/appointments?status=confirmed", headers=_headers(token))
        rejected_response = client.get("/api/v1/clients/me/appointments?status=rejected", headers=_headers(token))

    assert all_response.status_code == 200
    assert {item["client_id"] for item in all_response.json()} == {1}
    assert confirmed_response.status_code == 200
    assert [item["status"] for item in confirmed_response.json()] == ["confirmed"]
    assert rejected_response.status_code == 200
    assert rejected_response.json() == []


def test_partner_list_only_own_appointments_and_cannot_patch_other_partner() -> None:
    with _make_client() as client:
        token = _user_login(client, "partner@example.com", "PartnerPassword123")
        list_response = client.get("/api/v1/partners/me/appointments", headers=_headers(token))
        forbidden_patch_response = client.patch(
            "/api/v1/partners/me/appointments/2",
            json={"status": "confirmed"},
            headers=_headers(token),
        )

    assert list_response.status_code == 200
    assert {item["partner_id"] for item in list_response.json()} == {1}
    assert forbidden_patch_response.status_code == 404


def test_partner_status_transitions_timestamps_and_invalid_transition() -> None:
    with _make_client() as client:
        client_token = _user_login(client, "client@example.com", "ClientPassword123")
        partner_token = _user_login(client, "partner@example.com", "PartnerPassword123")
        created = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"client_phone": "+70000000001"},
            headers=_headers(client_token),
        ).json()
        appointment_id = created["id"]

        confirmed = client.patch(
            f"/api/v1/partners/me/appointments/{appointment_id}",
            json={"status": "confirmed", "comment": "  ok  "},
            headers=_headers(partner_token),
        )
        same_status = client.patch(
            f"/api/v1/partners/me/appointments/{appointment_id}",
            json={"status": "confirmed"},
            headers=_headers(partner_token),
        )
        completed = client.patch(
            f"/api/v1/partners/me/appointments/{appointment_id}",
            json={"status": "completed"},
            headers=_headers(partner_token),
        )
        invalid = client.patch(
            f"/api/v1/partners/me/appointments/{appointment_id}",
            json={"status": "cancelled"},
            headers=_headers(partner_token),
        )

        rejected_source = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"client_phone": "+70000000002"},
            headers=_headers(client_token),
        ).json()
        rejected = client.patch(
            f"/api/v1/partners/me/appointments/{rejected_source['id']}",
            json={"status": "rejected"},
            headers=_headers(partner_token),
        )
        cancelled_source = client.post(
            "/api/v1/clients/partners/1/appointments",
            json={"client_phone": "+70000000003"},
            headers=_headers(client_token),
        ).json()
        cancelled = client.patch(
            f"/api/v1/partners/me/appointments/{cancelled_source['id']}",
            json={"status": "cancelled"},
            headers=_headers(partner_token),
        )

    assert confirmed.status_code == 200
    assert confirmed.json()["confirmed_at"] is not None
    assert confirmed.json()["comment"] == "ok"
    assert same_status.status_code == 200
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None
    assert invalid.status_code == 400
    assert rejected.status_code == 200
    assert rejected.json()["rejected_at"] is not None
    assert cancelled.status_code == 200
    assert cancelled.json()["cancelled_at"] is not None


def test_admin_list_filters_limit_cap_and_patch_status() -> None:
    with _make_client() as client:
        admin_token = _admin_login(client)
        client_token = _user_login(client, "client@example.com", "ClientPassword123")
        non_admin_response = client.get("/api/v1/admin/appointments", headers=_headers(client_token))
        all_response = client.get("/api/v1/admin/appointments?limit=100", headers=_headers(admin_token))
        filtered_response = client.get(
            "/api/v1/admin/appointments?status=confirmed&partner_id=1&client_id=1&limit=500",
            headers=_headers(admin_token),
        )
        patched = client.patch(
            "/api/v1/admin/appointments/2",
            json={"status": "cancelled", "comment": " admin cancelled "},
            headers=_headers(admin_token),
        )
        missing = client.patch(
            "/api/v1/admin/appointments/999",
            json={"status": "cancelled"},
            headers=_headers(admin_token),
        )

    assert non_admin_response.status_code in {401, 403}
    assert all_response.status_code == 200
    assert len(all_response.json()) == 2
    assert filtered_response.status_code == 200
    assert [item["id"] for item in filtered_response.json()] == [1]
    assert patched.status_code == 200
    assert patched.json()["status"] == "cancelled"
    assert patched.json()["cancelled_at"] is not None
    assert patched.json()["comment"] == "admin cancelled"
    assert missing.status_code == 404


def test_activity_feeds_include_appointment_events_and_filter() -> None:
    with _make_client() as client:
        client_token = _user_login(client, "client@example.com", "ClientPassword123")
        partner_token = _user_login(client, "partner@example.com", "PartnerPassword123")
        admin_token = _admin_login(client)

        client_feed = client.get("/api/v1/clients/me/activity?limit=100", headers=_headers(client_token))
        partner_feed = client.get("/api/v1/partners/me/activity?limit=100", headers=_headers(partner_token))
        admin_feed = client.get("/api/v1/admin/activity?limit=100", headers=_headers(admin_token))
        filtered = client.get(
            "/api/v1/admin/activity?event_type=appointment_confirmed&limit=100",
            headers=_headers(admin_token),
        )

    assert client_feed.status_code == 200
    assert "appointment_created" in {item["event_type"] for item in client_feed.json()["items"]}
    assert partner_feed.status_code == 200
    assert {"appointment_created", "appointment_confirmed"}.issubset(
        {item["event_type"] for item in partner_feed.json()["items"]}
    )
    assert admin_feed.status_code == 200
    assert {"Alpha Beauty", "Beta Yoga"}.issubset({item["partner_name"] for item in admin_feed.json()["items"]})
    assert filtered.status_code == 200
    assert {item["event_type"] for item in filtered.json()["items"]} == {"appointment_confirmed"}


def test_partner_appointments_table_and_alembic_head() -> None:
    assert "partner_appointments" in Base.metadata.tables

    revisions: dict[str, str | None] = {}
    for path in Path("alembic/versions").glob("*.py"):
        module = ast.parse(path.read_text())
        revision = next(node for node in module.body if isinstance(node, ast.Assign) and node.targets[0].id == "revision")
        down_revision = next(
            node for node in module.body if isinstance(node, ast.Assign) and node.targets[0].id == "down_revision"
        )
        revisions[ast.literal_eval(revision.value)] = ast.literal_eval(down_revision.value)

    referenced_revisions = {down_revision for down_revision in revisions.values() if down_revision}
    assert sorted(set(revisions) - referenced_revisions) == ["20260518_0009"]
