# tests/guards/test_schema_public_surface_exports_guard.py
"""
Guardrail: any schema imported via `from schemas import X` in runtime code must be
exported in `schemas.__all__`.

Why:
- `schemas/__init__.py` is the public contract surface.
- If a schema isn't exported, developers tend to deep-import internal schema modules,
  violating the "no deep schema imports" rule and breaking refactors.

Scope:
- Scan apps/**/*.py (exclude tests).
- Static AST scan (no imports of app modules).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

import schemas


@dataclass(frozen=True)
class MissingExport:
    path: str
    lineno: int
    name: str
    line: str


def _iter_schema_imports(path: Path) -> list[tuple[int, str, str]]:
    """
    Returns (lineno, imported_name, source_line) for each `from schemas import X`.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text, filename=str(path))

    lines = text.splitlines()
    hits: list[tuple[int, str, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "schemas":
            # Disallow star-import in runtime code
            for alias in node.names:
                name = alias.name
                lineno = getattr(node, "lineno", 1)
                src_line = (
                    lines[lineno - 1].rstrip("\n") if 1 <= lineno <= len(lines) else ""
                )
                hits.append((lineno, name, src_line))

    return hits


def test_schemas_public_surface_exports_cover_runtime_imports() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    apps_root = repo_root / "apps"
    assert apps_root.exists(), f"Expected apps/ at: {apps_root}"

    exported = set(getattr(schemas, "__all__", []))
    assert exported, "schemas.__all__ is empty or missing"

    missing: list[MissingExport] = []

    for py_file in apps_root.rglob("*.py"):
        rel = py_file.relative_to(repo_root).as_posix()

        # Exclude tests
        if "/tests/" in rel or rel.endswith("_test.py") or rel.startswith("tests/"):
            continue

        # Exclude migrations (if present in your repo)
        if "/migrations/" in rel:
            continue

        for lineno, name, src_line in _iter_schema_imports(py_file):
            if name == "*":
                missing.append(
                    MissingExport(
                        path=rel,
                        lineno=lineno,
                        name="*",
                        line=src_line,
                    )
                )
                continue

            if name not in exported:
                missing.append(
                    MissingExport(
                        path=rel,
                        lineno=lineno,
                        name=name,
                        line=src_line,
                    )
                )

    if missing:
        formatted = "\n".join(
            f"{m.path}:{m.lineno}: `{m.name}` not in schemas.__all__  |  {m.line}"
            for m in missing
        )
        pytest.fail(
            "Public schema surface is incomplete.\n"
            "Fix by re-exporting missing names in schemas/__init__.py and adding them to __all__.\n\n"
            f"{formatted}"
        )
