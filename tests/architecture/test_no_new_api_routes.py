# tests/architecture/test_no_new_api_routes.py
from pathlib import Path

LEGACY_API_ROUTES_DIR = Path("api/routes")


def test_api_routes_is_legacy_and_does_not_grow():
    """
    Guardrail: real routes live under apps/<app>/routes/.
    api/routes/ may exist as shims only.
    """
    assert (
        LEGACY_API_ROUTES_DIR.exists()
    ), "api/routes/ missing (expected legacy/shims dir)"

    bad_files = []
    for p in LEGACY_API_ROUTES_DIR.glob("*.py"):
        if p.name in {"__init__.py"}:
            continue
        text = p.read_text(encoding="utf-8")

        # Shims are allowed to re-export a router, but must not define endpoints.
        if "@router." in text or "APIRouter(" in text:
            bad_files.append(p.as_posix())

    assert (
        not bad_files
    ), f"api/routes/ contains real routes (must be shims only): {bad_files}"
