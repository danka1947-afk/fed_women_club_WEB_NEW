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
from app.models.user import AdminUser, User, UserRole


@pytest.fixture()
def admin_users_client() -> Generator[TestClient, None, None]:
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
        session.add_all(
            [
                User(
                    email="existing-partner@example.com",
                    phone="+79990000001",
                    password_hash=hash_password("PartnerPassword123"),
                    role=UserRole.PARTNER.value,
                    is_active=True,
                ),
                User(
                    email="existing-client@example.com",
                    phone="+79990000002",
                    password_hash=hash_password("ClientPassword123"),
                    role=UserRole.CLIENT.value,
                    is_active=False,
                ),
                User(
                    email="manager@example.com",
                    phone="+79990000003",
                    password_hash=hash_password("AdminUserPassword123"),
                    role=UserRole.ADMIN.value,
                    is_active=True,
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
def admin_token(admin_users_client: TestClient) -> str:
    response = admin_users_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "email": "new-user@example.com",
        "phone": "+79990000009",
        "password": "NewPassword123",
        "role": "partner",
        "is_active": True,
    }
    payload.update(overrides)
    return payload


def test_admin_users_returns_401_without_token(admin_users_client: TestClient) -> None:
    response = admin_users_client.get("/api/v1/admin/users")

    assert response.status_code == 401


def test_admin_users_post_creates_partner_user_with_email_password(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json={"email": "  Partner.New@Example.COM  ", "password": "PartnerNew123", "role": "partner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 4
    assert data["email"] == "partner.new@example.com"
    assert data["phone"] is None
    assert data["role"] == "partner"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_admin_users_created_partner_can_login_via_user_login(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    create_response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json={"email": "login-partner@example.com", "password": "PartnerNew123", "role": "partner"},
    )
    assert create_response.status_code == 200

    login_response = admin_users_client.post(
        "/api/v1/auth/user-login",
        json={"login": "LOGIN-PARTNER@example.com", "password": "PartnerNew123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["role"] == "partner"


def test_admin_users_post_creates_client_user_with_phone_password(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json={"phone": "  +79990000999  ", "password": "ClientNew123", "role": "client"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] is None
    assert data["phone"] == "+79990000999"
    assert data["role"] == "client"


def test_admin_users_post_duplicate_email_returns_409(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json=_user_payload(email="existing-partner@example.com", phone="+79990001000"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email or phone already exists"


def test_admin_users_post_duplicate_phone_returns_409(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json=_user_payload(email="unique@example.com", phone="+79990000001"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email or phone already exists"


def test_admin_users_post_missing_email_and_phone_returns_400(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json={"email": " ", "phone": " ", "password": "NewPassword123", "role": "client"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email or phone is required"


def test_admin_users_post_invalid_role_returns_400(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json=_user_payload(role="owner"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user role"


def test_admin_users_post_short_password_returns_400(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.post(
        "/api/v1/admin/users",
        headers=_auth_headers(admin_token),
        json=_user_payload(password="short"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters"


def test_admin_users_list_filters_by_role(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.get("/api/v1/admin/users?role=partner", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [user["email"] for user in data] == ["existing-partner@example.com"]


def test_admin_users_list_filters_by_is_active(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.get("/api/v1/admin/users?is_active=false", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [user["email"] for user in data] == ["existing-client@example.com"]


def test_admin_users_list_q_search_works(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.get("/api/v1/admin/users?q=000003", headers=_auth_headers(admin_token))

    assert response.status_code == 200
    data = response.json()
    assert [user["email"] for user in data] == ["manager@example.com"]


def test_admin_users_patch_updates_email_phone_role_is_active(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.patch(
        "/api/v1/admin/users/1",
        headers=_auth_headers(admin_token),
        json={
            "email": "  UPDATED@Example.COM ",
            "phone": " +79990001111 ",
            "role": "client",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "updated@example.com"
    assert data["phone"] == "+79990001111"
    assert data["role"] == "client"
    assert data["is_active"] is False


def test_admin_users_patch_updates_password_and_rotates_login(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.patch(
        "/api/v1/admin/users/1",
        headers=_auth_headers(admin_token),
        json={"password": "UpdatedPassword123"},
    )
    assert response.status_code == 200

    old_login_response = admin_users_client.post(
        "/api/v1/auth/user-login",
        json={"login": "existing-partner@example.com", "password": "PartnerPassword123"},
    )
    new_login_response = admin_users_client.post(
        "/api/v1/auth/user-login",
        json={"login": "existing-partner@example.com", "password": "UpdatedPassword123"},
    )

    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200


def test_admin_users_patch_cannot_clear_both_email_and_phone(
    admin_users_client: TestClient,
    admin_token: str,
) -> None:
    response = admin_users_client.patch(
        "/api/v1/admin/users/1",
        headers=_auth_headers(admin_token),
        json={"email": None, "phone": " "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email or phone is required"


def test_admin_users_patch_missing_user_returns_404(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.patch(
        "/api/v1/admin/users/9999",
        headers=_auth_headers(admin_token),
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"



def test_admin_users_delete_requires_admin_token(admin_users_client: TestClient) -> None:
    response = admin_users_client.delete('/api/v1/admin/users/1')
    assert response.status_code == 401


def test_admin_users_delete_missing_user_returns_404(admin_users_client: TestClient, admin_token: str) -> None:
    response = admin_users_client.delete('/api/v1/admin/users/9999', headers=_auth_headers(admin_token))
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_admin_users_delete_client_user_and_related_records(admin_users_client: TestClient, admin_token: str) -> None:
    create_user = admin_users_client.post(
        '/api/v1/admin/users', headers=_auth_headers(admin_token), json={'email': 'vk-client@example.com', 'password': 'ClientVk123', 'role': 'client'}
    )
    assert create_user.status_code == 200
    user_id = create_user.json()['id']

    response = admin_users_client.delete(f'/api/v1/admin/users/{user_id}', headers=_auth_headers(admin_token))
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] is True
    assert data['deleted_user_id'] == user_id
    assert 'deleted' in data
    assert data['deleted']['user'] == 1


def test_admin_users_delete_cannot_delete_self(admin_users_client: TestClient, admin_token: str) -> None:
    create_user = admin_users_client.post(
        '/api/v1/admin/users', headers=_auth_headers(admin_token), json={'email': 'admin@example.com', 'password': 'AdminRole123', 'role': 'client'}
    )
    assert create_user.status_code == 200

    response = admin_users_client.delete(f"/api/v1/admin/users/{create_user.json()['id']}", headers=_auth_headers(admin_token))
    assert response.status_code == 400
    assert response.json()['detail'] == 'Нельзя удалить самого себя'


def test_admin_users_delete_cannot_delete_last_admin_role_user(admin_users_client: TestClient, admin_token: str) -> None:
    create_response = admin_users_client.post(
        '/api/v1/admin/users', headers=_auth_headers(admin_token), json={'email': 'extra-admin@example.com', 'password': 'AdminRole123', 'role': 'admin'}
    )
    assert create_response.status_code == 200
    extra_admin_id = create_response.json()['id']

    response = admin_users_client.delete(f'/api/v1/admin/users/{extra_admin_id}', headers=_auth_headers(admin_token))
    assert response.status_code == 200

    response = admin_users_client.delete('/api/v1/admin/users/3', headers=_auth_headers(admin_token))
    assert response.status_code == 400
    assert response.json()['detail'] == 'Нельзя удалить последнего администратора'
