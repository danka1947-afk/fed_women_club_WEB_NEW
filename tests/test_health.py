from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_app_is_fastapi_asgi_application() -> None:
    assert isinstance(app, FastAPI)
    assert callable(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
