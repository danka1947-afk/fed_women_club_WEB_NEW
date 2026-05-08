from app.core.config import settings


def test_cors_origins_are_split() -> None:
    assert "http://localhost:5173" in settings.backend_cors_origins_list
