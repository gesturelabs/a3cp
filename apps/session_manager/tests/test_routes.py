# apps/session_manager/tests/test_routes.py

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_session_manager_routes_are_mounted():
    # This should fail validation (422) because payload is missing,
    # which proves the route exists and is wired.
    resp = client.post("/session_manager/sessions.start", json={})
    assert resp.status_code in (400, 422)
