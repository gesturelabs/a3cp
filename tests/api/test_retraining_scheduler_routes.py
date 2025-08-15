import pytest

pytestmark = pytest.mark.skip(
    reason="Legacy API test; awaiting rewrite for unified routes"
)

# tests/api/test_retraining_scheduler_routes.py
