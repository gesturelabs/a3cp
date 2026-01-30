# apps/schema_recorder/config.py

from __future__ import annotations

from pathlib import Path

# Absolute or repo-relative root for logs (intentionally patchable in tests)
LOG_ROOT = Path("logs")  # default for dev/demo; tests must override to tmp_path
