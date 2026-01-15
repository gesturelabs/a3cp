# tests/guards/test_raw_session_log_path_guard.py


"""
Guardrail: raw session-log paths must not be hardcoded outside schema_recorder.

Why:
- Session JSONL layout is a security- and integrity-critical invariant.
- Hardcoding paths like `logs/users/.../sessions/*.jsonl` bypasses:
  - single-writer enforcement
  - locking
  - size limits
  - audit guarantees
- All path construction must go through utils.paths.session_log_path()
  and all writes through schema_recorder.repository.

This is a fast static scan:
- no imports
- no filesystem mutation
- fails loudly with file + line number
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

# Patterns that indicate hardcoded session-log paths
TOKENS = (
    "logs/users/",
    "/sessions/",
    "sessions/",
    ".jsonl",
)

# Files explicitly allowed to mention these patterns
ALLOWLIST = {
    "apps/schema_recorder/repository.py",
    "apps/schema_recorder/service.py",
    "utils/paths.py",  # canonical path constructor
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
                    Hit(
                        path=path,
                        lineno=i,
                        token=token,
                        line=line.rstrip("\n"),
                    )
                )
    return hits


def test_no_raw_session_log_paths_outside_allowlist() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    apps_root = repo_root / "apps"
    assert apps_root.exists(), f"Expected apps/ directory at: {apps_root}"

    hits: list[Hit] = []

    for py_file in apps_root.rglob("*.py"):
        rel_path = py_file.relative_to(repo_root).as_posix()

        # Exclude test trees under apps/*/tests/
        if "/tests/" in rel_path or rel_path.endswith("/tests.py"):
            continue

        if rel_path in ALLOWLIST:
            continue

        hits.extend(_scan_file(py_file))

    if hits:
        formatted = "\n".join(
            f"{h.path.relative_to(repo_root)}:{h.lineno}: "
            f"contains '{h.token}': {h.line}"
            for h in hits
        )
        pytest.fail(
            "Raw session-log path or JSONL pattern detected outside allowlist.\n"
            "All session log paths must be constructed via utils.paths.session_log_path(),\n"
            "and all writes must go through schema_recorder.\n\n"
            f"{formatted}"
        )
