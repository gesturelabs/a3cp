# apps/camera_feed_worker/tests/conftest.py
from __future__ import annotations

from datetime import datetime, timezone

import pytest


@pytest.fixture(scope="module")
def connection_key() -> str:
    return "conn_test"


@pytest.fixture(scope="module")
def now_ingest() -> datetime:
    # Stable, UTC-aware default ingest timestamp
    return datetime(2026, 2, 4, 12, 0, 0, tzinfo=timezone.utc)
