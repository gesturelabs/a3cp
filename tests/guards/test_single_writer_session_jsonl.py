# tests/guards/test_single_writer_session_jsonl.py

"""
Guardrail: single-writer invariant for session JSONL logs.

Invariant:
  Only `apps/schema_recorder/repository.py` may contain code that appears to write
  session-scoped JSONL logs (logs/users/<user_id>/sessions/<session_id>.jsonl).

Rationale:
  Session logs are append-only, ordered, and locked. Allowing ad-hoc writers in other
  modules is a high-risk integrity regression.

Approach:
  Fast static scan (no imports). Flag files that contain BOTH:
    (A) session-log signature patterns AND
    (B) write/lock primitives
  unless the file is explicitly allowlisted.

Notes:
  This is intentionally conservative and may be tightened over time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

# --- Configuration (single source of truth) ---

# Explicit allowlist: only these files may contain session JSONL write patterns.
ALLOWLIST = {
    Path("apps/schema_recorder/repository.py"),
}

# Scan scope: keep it narrow and meaningful.
SCAN_ROOTS = [
    Path("apps"),
    Path("api"),
]

# Heuristics to detect "this file is probably writing session JSONL logs"
SESSION_LOG_SIGNATURES = (
    "logs/users/",
    "/sessions/",
    "sessions/",
    ".jsonl",
    "session_log_path(",
)

WRITE_OR_LOCK_PRIMITIVES = (
    "open(",
    ".open(",
    "Path.open(",
    "os.open(",
    "os.write(",
    "fcntl.flock(",
    "O_APPEND",
)


# --- Implementation ---


@dataclass(frozen=True)
class Hit:
    path: Path
    lineno: int
    line: str


def iter_python_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            # Skip typical noise dirs if they ever appear under roots
            parts = set(p.parts)
            if {"__pycache__", ".pytest_cache", ".ruff_cache"} & parts:
                continue
            yield p


def file_has_any(text: str, needles: Tuple[str, ...]) -> bool:
    return any(n in text for n in needles)


def find_hits(path: Path, needles: Tuple[str, ...]) -> List[Hit]:
    hits: List[Hit] = []
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # If a file isn't utf-8, treat that as "not scanned" rather than failing the suite.
        return hits

    for i, line in enumerate(content.splitlines(), start=1):
        if any(n in line for n in needles):
            hits.append(Hit(path=path, lineno=i, line=line.rstrip()))
    return hits


def test_single_writer_for_session_jsonl() -> None:
    violations: List[Tuple[Path, List[Hit]]] = []

    for path in iter_python_files(SCAN_ROOTS):
        rel = path.as_posix()
        rel_path = Path(rel)

        # Normalize to repo-relative paths
        try:
            rel_path = path.relative_to(Path.cwd())
        except ValueError:
            # If running from a different CWD, fall back to given path
            rel_path = Path(rel)

        if rel_path in ALLOWLIST:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        # Require BOTH a session-log signature and a write/lock primitive to reduce false positives.
        has_sig = file_has_any(text, SESSION_LOG_SIGNATURES)
        has_io = file_has_any(text, WRITE_OR_LOCK_PRIMITIVES)

        if has_sig and has_io:
            # Collect a few helpful lines for debugging
            sig_hits = find_hits(path, SESSION_LOG_SIGNATURES)
            io_hits = find_hits(path, WRITE_OR_LOCK_PRIMITIVES)
            sample = (sig_hits + io_hits)[:20]
            violations.append((rel_path, sample))

    if violations:
        msg_lines = [
            "Single-writer invariant violated: session JSONL write patterns found outside allowlist.",
            "",
            f"ALLOWLIST ({len(ALLOWLIST)}):",
            *[f"  - {p.as_posix()}" for p in sorted(ALLOWLIST)],
            "",
            "Violations:",
        ]
        for bad_path, hits in violations:
            msg_lines.append(f"\n- {bad_path.as_posix()}")
            for h in hits:
                # Display file-relative line numbers for quick navigation
                msg_lines.append(f"    L{h.lineno}: {h.line}")
        raise AssertionError("\n".join(msg_lines))
