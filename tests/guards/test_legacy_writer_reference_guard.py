# tests/guards/test_legacy_writer_reference_guard.py

"""
Guardrail: legacy session writer references must not exist in runtime code.

Why:
- A3CP has a single-writer invariant for session JSONL: only schema_recorder may append.
- Legacy helpers like `append_session_event` / `session_writer` are easy to accidentally reintroduce
  via copy/paste or old branches.
- This test is a fast static scan (no imports, no IO mutation) that fails loudly with file+line.

Scope:
- Scan only Python files under `apps/`
- Ignore non-.py files implicitly (md/txt not scanned)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

TOKENS = ("append_session_event", "session_writer")


@dataclass(frozen=True)
class Hit:
    path: Path
    lineno: int
    token: str
    line: str


def _scan_file(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    # utf-8 with replacement keeps the guard resilient to odd encodings
    text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), start=1):
        for token in TOKENS:
            if token in line:
                hits.append(
                    Hit(path=path, lineno=i, token=token, line=line.rstrip("\n"))
                )
    return hits


def test_no_legacy_writer_references_in_apps_tree() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    apps_root = repo_root / "apps"
    assert apps_root.exists(), f"Expected apps/ directory at: {apps_root}"

    hits: list[Hit] = []
    for py_file in apps_root.rglob("*.py"):
        hits.extend(_scan_file(py_file))

    if hits:
        formatted = "\n".join(
            f"{h.path.relative_to(repo_root)}:{h.lineno}: contains '{h.token}': {h.line}"
            for h in hits
        )
        pytest.fail(
            "Legacy writer reference(s) detected in apps/ tree. "
            "Remove these references and route all session JSONL appends via schema_recorder.\n\n"
            f"{formatted}"
        )
