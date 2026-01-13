# apps/schema_recorder/tests/test_guardrails.py

from __future__ import annotations

import ast
from pathlib import Path


def test_schema_recorder_route_imports_only_public_schemas_surface() -> None:
    """
    Guardrail: schema_recorder route files must not deep-import schemas.*.
    They must import only via: `from schemas import ...`.
    """
    route_file = Path("apps/schema_recorder/routes/router.py")
    src = route_file.read_text(encoding="utf-8")
    tree = ast.parse(src)

    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            # Disallow: from schemas.<submodule> import ...
            if node.module.startswith("schemas."):
                bad.append((node.lineno, f"from {node.module} import ..."))

        if isinstance(node, ast.Import):
            for alias in node.names:
                # Disallow: import schemas.<submodule>
                if alias.name.startswith("schemas."):
                    bad.append((node.lineno, f"import {alias.name}"))

    assert not bad, f"Deep schema imports found: {bad}"


def test_public_schema_surface_exports_a3cpmessage() -> None:
    """
    Guardrail: route-required schemas must exist on public surface.
    """
    from schemas import __all__ as public_all  # noqa: WPS433 (test imports)

    assert "A3CPMessage" in public_all
