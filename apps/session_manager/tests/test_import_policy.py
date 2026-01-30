# apps/session_manager/tests/test_import_policy.py
import inspect
import pathlib
import re

import apps.session_manager.service as sm_service


def test_session_manager_route_does_not_deep_import_schema_submodules() -> None:
    """
    Scoped guardrail (session_manager only):
    session_manager routes must import schemas only via:
        from schemas import ...
    and must NOT deep-import:
        from schemas.<submodule> import ...
        import schemas.<submodule>
    """
    route_file = pathlib.Path("apps/session_manager/routes/router.py")
    assert route_file.exists(), "apps/session_manager/routes/router.py not found"

    text = route_file.read_text(encoding="utf-8")

    deep_from = re.compile(r"^\s*from\s+schemas\.[\w.]+\s+import\s+", re.MULTILINE)
    deep_import = re.compile(r"^\s*import\s+schemas\.[\w.]+", re.MULTILINE)

    assert not deep_from.search(
        text
    ), "session_manager_routes.py has a deep 'from schemas.<submodule> import ...'"
    assert not deep_import.search(
        text
    ), "session_manager_routes.py has a deep 'import schemas.<submodule>'"


def test_session_manager_service_does_not_implement_direct_jsonl_writes():
    src = inspect.getsource(sm_service)

    # guardrails: session_manager must delegate appends to schema_recorder.append_event
    assert "append_event(" in src

    # forbid obvious direct write patterns
    forbidden_tokens = [
        ".open(",
        "Path.open(",
        "open(",
        "write(",
        ".write_text(",
        ".write_bytes(",
    ]
    # allow read-only patterns elsewhere, but service should not contain write calls
    for tok in forbidden_tokens:
        assert tok not in src, f"forbidden token in session_manager.service.py: {tok}"


def test_session_manager_service_does_not_import_schema_recorder_repository() -> None:
    """
    Writer-boundary guardrail:
    session_manager must not import schema_recorder.repository (low-level writer).
    It must only call schema_recorder.service.append_event().
    """
    service_file = pathlib.Path("apps/session_manager/service.py")
    assert service_file.exists(), "apps/session_manager/service.py not found"

    text = service_file.read_text(encoding="utf-8")

    assert "apps.schema_recorder.repository" not in text
    assert "import apps.schema_recorder.repository" not in text
    assert "from apps.schema_recorder.repository" not in text
