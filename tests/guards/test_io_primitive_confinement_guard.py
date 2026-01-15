"""
Guardrail: recording IO primitives are confined to schema_recorder.repository only.

Why:
- A3CP enforces a single-writer invariant for session JSONL.
- The low-level primitives that can bypass the recorder's guarantees (locking, append semantics,
  atomic one-line writes) must not appear elsewhere in runtime apps.
- This guard prevents reintroducing direct file writes via open/os.open/os.write/flock/etc.

Scope:
- Scan Python files under apps/
- Exclude apps/**/tests/** (tests may legitimately use filesystem primitives)
- Allowlist ONLY: apps/schema_recorder/repository.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

# Keep these as simple substrings; this is a copy/paste prevention guard.
TOKENS = (
    "open(",  # built-in open(
    "Path.open(",  # pathlib Path.open(
    "os.open(",  # low-level open
    "os.write(",  # low-level write
    "fcntl.flock(",  # locking primitive
)

ALLOWLIST = {
    "apps/schema_recorder/repository.py",
}


@dataclass(frozen=True)
class Hit:
    path: Path
    lineno: int
    token: str
    line: str


def _scan_file(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), start=1):
        for token in TOKENS:
            if token in line:
                hits.append(
                    Hit(path=path, lineno=i, token=token, line=line.rstrip("\n"))
                )
    return hits


def test_io_primitives_confined_to_schema_recorder_repository() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    apps_root = repo_root / "apps"
    assert apps_root.exists(), f"Expected apps/ directory at: {apps_root}"

    hits: list[Hit] = []

    for py_file in apps_root.rglob("*.py"):
        rel = py_file.relative_to(repo_root).as_posix()

        # Exclude app-local tests
        if "/tests/" in rel or rel.endswith("/tests.py"):
            continue

        if rel in ALLOWLIST:
            continue

        hits.extend(_scan_file(py_file))

    if hits:
        formatted = "\n".join(
            f"{h.path.relative_to(repo_root)}:{h.lineno}: contains '{h.token}': {h.line}"
            for h in hits
        )
        pytest.fail(
            "Disallowed IO primitive(s) detected outside schema_recorder.repository.\n"
            "All session JSONL recording must go through schema_recorder, and low-level\n"
            "recording IO must remain confined to apps/schema_recorder/repository.py.\n\n"
            f"{formatted}"
        )
