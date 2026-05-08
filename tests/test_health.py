from __future__ import annotations

import asyncio

from app.main import health_check


def test_health_check() -> None:
    assert asyncio.run(health_check()) == {"status": "ok"}
