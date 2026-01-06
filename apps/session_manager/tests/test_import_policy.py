# apps/session_manager/tests/test_import_policy.py
import pathlib
import re


def test_session_manager_route_does_not_deep_import_schema_submodules() -> None:
    """
    Scoped guardrail (session_manager only):
    session_manager routes must import schemas only via:
        from schemas import ...
    and must NOT deep-import:
        from schemas.<submodule> import ...
        import schemas.<submodule>
    """
    route_file = pathlib.Path("api/routes/session_manager_routes.py")
    assert route_file.exists(), "api/routes/session_manager_routes.py not found"

    text = route_file.read_text(encoding="utf-8")

    deep_from = re.compile(r"^\s*from\s+schemas\.[\w.]+\s+import\s+", re.MULTILINE)
    deep_import = re.compile(r"^\s*import\s+schemas\.[\w.]+", re.MULTILINE)

    assert not deep_from.search(
        text
    ), "session_manager_routes.py has a deep 'from schemas.<submodule> import ...'"
    assert not deep_import.search(
        text
    ), "session_manager_routes.py has a deep 'import schemas.<submodule>'"
