# apps/session_manager/repository.py


import os
from pathlib import Path

from apps.schema_recorder import append_session_event as _append_session_event
from schemas import RecorderConfig


def append_session_event(*, user_id: str, session_id: str, message) -> None:
    cfg = RecorderConfig(
        log_format="jsonl",
        log_dir=Path(os.getenv("LOG_ROOT", "./logs")),
        enable_hashing=True,
        max_file_size_mb=None,
        allow_schema_override=False,
    )

    _append_session_event(
        cfg=cfg,
        user_id=user_id,
        session_id=session_id,
        message=message,
    )
