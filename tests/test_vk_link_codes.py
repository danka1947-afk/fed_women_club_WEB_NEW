from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all SQLAlchemy models for test metadata
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.client import ClientProfile, VkLinkCode, VkLinkCodeStatus
from app.models.user import User, UserRole

BOT_API_TOKEN = "test-vk-bot-service-token"


@pytest.fixture()
def vk_link_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    Base.metadata.create_all(bind=engine)
    with session_factory() as session:
        session.add_all(
            [
                User(
                    email="client@example.com",
                    phone="+79990000001",
                    password_hash=hash_password("ClientPassword123"),
                    role=UserRole.CLIENT.value,
                    is_active=True,
                ),
                User(
                    email="other@example.com",
                    phone="+79990000002",
                    password_hash=hash_password("OtherPassword123"),
                    role=UserRole.CLIENT.value,
                    is_active=True,
                ),
            ]
        )
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    old_token = settings.BOT_API_TOKEN
    object.__setattr__(settings, "BOT_API_TOKEN", BOT_API_TOKEN)
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        object.__setattr__(settings, "BOT_API_TOKEN", old_token)
        engine.dispose()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _bot_headers(token: str = BOT_API_TOKEN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user_login(client: TestClient, login: str = "client@example.com", password: str = "ClientPassword123") -> str:
    response = client.post("/api/v1/auth/user-login", json={"login": login, "password": password})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _create_code(client: TestClient) -> str:
    token = _user_login(client)
    response = client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token))
    assert response.status_code == 200
    return str(response.json()["code"])


def _db_session() -> Session:
    return next(app.dependency_overrides[get_db]())


def test_create_vk_link_code_without_token_returns_401(vk_link_client: TestClient) -> None:
    response = vk_link_client.post("/api/v1/clients/me/vk-link-codes")

    assert response.status_code == 401


def test_client_creates_vk_link_code(vk_link_client: TestClient) -> None:
    token = _user_login(vk_link_client)

    response = vk_link_client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert len(data["code"]) == 8
    assert data["code"].isalnum()
    assert data["code"] == data["code"].upper()
    assert data["status"] == "active"
    assert data["expires_at"]
    assert 0 < data["ttl_seconds"] <= 600


def test_creating_second_code_cancels_previous_active_code(vk_link_client: TestClient) -> None:
    token = _user_login(vk_link_client)
    first = vk_link_client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token)).json()["code"]
    second = vk_link_client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token)).json()["code"]

    assert first != second
    with _db_session() as session:
        first_code = session.execute(select(VkLinkCode).where(VkLinkCode.code == first)).scalar_one()
        second_code = session.execute(select(VkLinkCode).where(VkLinkCode.code == second)).scalar_one()
        assert first_code.status == VkLinkCodeStatus.CANCELLED.value
        assert second_code.status == VkLinkCodeStatus.ACTIVE.value


def test_bot_exchange_without_service_token_returns_401(vk_link_client: TestClient) -> None:
    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        json={"vk_user_id": "123", "code": "ABC12345"},
    )

    assert response.status_code == 401


def test_bot_exchange_with_wrong_service_token_returns_401(vk_link_client: TestClient) -> None:
    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers("wrong-token"),
        json={"vk_user_id": "123", "code": "ABC12345"},
    )

    assert response.status_code == 401


def test_bot_exchange_valid_code_links_vk_and_returns_working_token(vk_link_client: TestClient) -> None:
    code = _create_code(vk_link_client)

    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "  vk-123  ", "code": f"  {code.lower()}  "},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "client@example.com"
    with _db_session() as session:
        profile = session.execute(select(ClientProfile).where(ClientProfile.vk_user_id == "vk-123")).scalar_one()
        link_code = session.execute(select(VkLinkCode).where(VkLinkCode.code == code)).scalar_one()
        assert profile.vk_user_id == "vk-123"
        assert link_code.status == VkLinkCodeStatus.USED.value
        assert link_code.used_at is not None

    me_response = vk_link_client.get("/api/v1/auth/user-me", headers=_auth_headers(data["access_token"]))
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "client@example.com"


def test_exchange_missing_code_returns_404(vk_link_client: TestClient) -> None:
    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "123", "code": "missing"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Link code not found"


def test_exchange_expired_code_marks_expired_and_returns_400(vk_link_client: TestClient) -> None:
    code = _create_code(vk_link_client)
    with _db_session() as session:
        link_code = session.execute(select(VkLinkCode).where(VkLinkCode.code == code)).scalar_one()
        link_code.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.commit()

    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "123", "code": code},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Link code expired"
    with _db_session() as session:
        link_code = session.execute(select(VkLinkCode).where(VkLinkCode.code == code)).scalar_one()
        assert link_code.status == VkLinkCodeStatus.EXPIRED.value


def test_exchange_used_or_cancelled_code_returns_400(vk_link_client: TestClient) -> None:
    used_code = _create_code(vk_link_client)
    used_response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "123", "code": used_code},
    )
    assert used_response.status_code == 200

    used_again_response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "123", "code": used_code},
    )
    assert used_again_response.status_code == 400
    assert used_again_response.json()["detail"] == "Link code is not active"

    token = _user_login(vk_link_client)
    cancelled_code = vk_link_client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token)).json()["code"]
    vk_link_client.post("/api/v1/clients/me/vk-link-codes", headers=_auth_headers(token))
    cancelled_response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "456", "code": cancelled_code},
    )
    assert cancelled_response.status_code == 400
    assert cancelled_response.json()["detail"] == "Link code is not active"


def test_exchange_empty_vk_user_id_returns_400(vk_link_client: TestClient) -> None:
    code = _create_code(vk_link_client)

    response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "   ", "code": code},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "VK user ID is required"


def test_bot_vk_token_returns_token_for_linked_vk_user_id(vk_link_client: TestClient) -> None:
    code = _create_code(vk_link_client)
    exchange_response = vk_link_client.post(
        "/api/v1/bot/vk/exchange-link-code",
        headers=_bot_headers(),
        json={"vk_user_id": "vk-linked", "code": code},
    )
    assert exchange_response.status_code == 200

    response = vk_link_client.post(
        "/api/v1/bot/vk/token",
        headers=_bot_headers(),
        json={"vk_user_id": " vk-linked "},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    me_response = vk_link_client.get("/api/v1/clients/me", headers=_auth_headers(data["access_token"]))
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "client@example.com"


def test_bot_vk_token_returns_404_for_unlinked_vk_user_id(vk_link_client: TestClient) -> None:
    response = vk_link_client.post(
        "/api/v1/bot/vk/token",
        headers=_bot_headers(),
        json={"vk_user_id": "not-linked"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "VK user is not linked"
