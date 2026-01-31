# apps/session_manager/tests/test_route_error_mapping_policy.py

import importlib
import inspect


def test_session_routes_map_typed_exceptions_explicitly():
    router_module = importlib.import_module("apps.session_manager.routes.router")
    src = inspect.getsource(router_module)

    assert "except service.SessionAlreadyActive" in src
    assert "except service.SessionNotFound" in src
    assert "except service.SessionUserMismatch" in src
    assert "except service.SessionAlreadyClosed" in src

    forbidden = [
        "except ValueError",
        'if "not found" in',
        'if "mismatch" in',
        'if "closed" in',
    ]
    for tok in forbidden:
        assert tok not in src, f"Forbidden heuristic mapping pattern found: {tok}"
