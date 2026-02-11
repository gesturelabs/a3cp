# apps/camera_feed_worker/tests/test_ws_smoke.py

from fastapi.testclient import TestClient
from starlette.routing import Mount, WebSocketRoute

from main import app  # keep your standard import


def _routes_of(obj):
    router = getattr(obj, "router", None)
    return getattr(router, "routes", None)


def _collect_ws_paths(obj, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    routes = _routes_of(obj)
    if not routes:
        return paths  # e.g. StaticFiles mount

    for r in routes:
        if isinstance(r, WebSocketRoute):
            paths.add(prefix + r.path)
            continue

        if isinstance(r, Mount):
            sub_app = getattr(r, "app", None)
            if sub_app is None:
                continue
            paths |= _collect_ws_paths(sub_app, prefix + r.path)

    return paths


def _pick_ws_path() -> str:
    paths = _collect_ws_paths(app)
    for candidate in ("/camera_feed_worker/ws", "/api/camera_feed_worker/ws"):
        if candidate in paths:
            return candidate
    raise AssertionError(f"WS route not found. Discovered WS paths: {sorted(paths)}")


def test_app_boots_cleanly() -> None:
    assert app is not None


def test_ws_route_registered() -> None:
    paths = _collect_ws_paths(app)
    assert (
        "/camera_feed_worker/ws" in paths or "/api/camera_feed_worker/ws" in paths
    ), f"Missing ws route. Discovered WS paths: {sorted(paths)}"
    assert (
        "/camera_feed_worker/capture" in paths
        or "/api/camera_feed_worker/capture" in paths
    ), f"Missing capture route. Discovered WS paths: {sorted(paths)}"


def test_ws_basic_connect_succeeds() -> None:
    client = TestClient(app)
    ws_path = _pick_ws_path()
    with client.websocket_connect(ws_path):
        pass
