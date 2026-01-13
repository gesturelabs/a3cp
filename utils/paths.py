from __future__ import annotations

from pathlib import Path
from typing import Any


def session_log_path(log_root: Path, user_id: Any, session_id: Any) -> Path:
    """
    Pure path helper (NO IO, NO env reads, NO mkdir).

    Canonical layout:
      <LOG_ROOT>/users/<user_id>/sessions/<session_id>.jsonl
    """
    if not isinstance(log_root, Path):
        raise TypeError("log_root must be a pathlib.Path")

    # Treat ids as opaque segments; no validation here (validation belongs upstream).
    user_seg = str(user_id)
    session_seg = str(session_id)

    return log_root / "users" / user_seg / "sessions" / f"{session_seg}.jsonl"
