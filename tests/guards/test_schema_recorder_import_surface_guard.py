# tests/guards/test_schema_recorder_import_surface_guard.py
"""
Guardrail: schema_recorder must import schemas only from the public `schemas` surface.

Why:
- `schemas/` defines the stable, public contract boundary.
- Deep imports (e.g. schemas.base.base, schemas.a3cp_message.a3cp_message)
  couple runtime code to internal layout and break refactors, versioning,
  and schema registry guarantees.
- This guard ensures architectural hygiene at the module boundary.

Scope:
- Scan only apps/schema_recorder/**/*.py
- Static text scan (no imports, no execution)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

# Any import that references schemas.* beyond the top-level surface is forbidden.
FORBIDDEN_PREFIXES = ("schemas.",)

# Allowed exact imports from schemas surface
ALLOWED_IMPORTS = (
    "from schemas import",
    "import schemas",
)

# Files allowed to contain deep schema references (should normally be empty)
ALLOWLIST: set[str] = set()


@dataclass(frozen=True)
class Hit:
    path: Path
    lineno: int
    line: str


def _is_forbidden_schema_import(line: str) -> bool:
    stripped = line.strip()

    if not (stripped.startswith("import ") or stripped.startswith("from ")):
        return False

    # Allow explicit surface imports
    for allowed in ALLOWED_IMPORTS:
        if stripped.startswith(allowed):
            return False

    # Forbid any deep schemas.* reference
    return any(prefix in stripped for prefix in FORBIDDEN_PREFIXES)


def _scan_file(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), start=1):
        if _is_forbidden_schema_import(line):
            hits.append(Hit(path=path, lineno=i, line=line.rstrip("\n")))
    return hits


def test_schema_recorder_uses_only_public_schema_surface() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sr_root = repo_root / "apps" / "schema_recorder"
    assert sr_root.exists(), f"Expected schema_recorder app at: {sr_root}"

    hits: list[Hit] = []

    for py_file in sr_root.rglob("*.py"):
        rel = py_file.relative_to(repo_root).as_posix()

        # Exclude tests
        if "/tests/" in rel or rel.endswith("/tests.py"):
            continue

        if rel in ALLOWLIST:
            continue

        hits.extend(_scan_file(py_file))

    if hits:
        formatted = "\n".join(
            f"{h.path.relative_to(repo_root)}:{h.lineno}: {h.line}" for h in hits
        )
        pytest.fail(
            "schema_recorder imports schemas via deep/private paths.\n"
            "Only public surface imports are allowed, e.g. `from schemas import A3CPMessage`.\n\n"
            f"{formatted}"
        )
