# apps/schema_recorder/session_writer.py

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Protocol

from schemas.schema_recorder.schema_recorder import RecorderConfig


class _Jsonable(Protocol):
    def model_dump(self, *args: Any, **kwargs: Any) -> dict: ...


def session_log_path(*, cfg: RecorderConfig, user_id: str, session_id: str) -> Path:
    """
    Resolve LOG_ROOT at call time, not import time.
    """
    log_root = Path(os.getenv("LOG_ROOT", cfg.log_dir))
    return log_root / "users" / user_id / "sessions" / f"{session_id}.jsonl"


def append_session_event(
    *, cfg: RecorderConfig, user_id: str, session_id: str, message: _Jsonable
) -> Path:
    """
    Append exactly one schema record (A3CPMessage-compatible) as one JSONL line.

    This is intended to be the only allowlisted writer for:
      logs/users/**/sessions/*.jsonl
    """
    path = session_log_path(cfg=cfg, user_id=user_id, session_id=session_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = message.model_dump(mode="json")

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False))
        f.write("\n")

    return path
