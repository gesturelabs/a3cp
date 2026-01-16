# apps/schema_recorder/repository.py

from __future__ import annotations

import errno
import fcntl
import os
from pathlib import Path

from apps.schema_recorder.service import MissingSessionPath, RecorderIOError


def append_bytes(*, log_path: Path, line_bytes: bytes) -> None:
    """
    Append exactly one JSONL line (newline-terminated) to `log_path`.

    Locked MVP invariants:
      - No mkdir here (session_manager must create directories)
      - May create the <session_id>.jsonl file iff parent directory exists
      - OS-level lock MUST be flock(LOCK_EX) on the session file descriptor
      - Lock held across: open -> write -> close
      - Open with append semantics (O_APPEND)
      - Write the full line using a single OS write() call (no chunking)
      - No fsync in MVP

    Raises:
      - MissingSessionPath if parent dir missing
      - RecorderIOError for all other OS/FS failures
    """
    _ensure_parent_exists(log_path)

    data = _ensure_newline(line_bytes)
    data = _ensure_newline(line_bytes)
    _reject_embedded_newlines(data)

    fd: int | None = None
    try:
        fd = _open_append_fd(log_path)
        _lock_fd(fd)
        _write_all(fd, data, log_path)
    except MissingSessionPath:
        raise
    except OSError as e:
        _raise_mapped_os_error(e, log_path)
    except RecorderIOError:
        raise
    except Exception as e:
        raise RecorderIOError(f"{type(e).__name__}: {e}") from e
    finally:
        _best_effort_close(fd)


def _ensure_parent_exists(log_path: Path) -> None:
    parent = log_path.parent
    if not parent.exists():
        raise MissingSessionPath(f"Missing parent session directory: {parent}")


def _ensure_newline(line_bytes: bytes) -> bytes:
    return line_bytes if line_bytes.endswith(b"\n") else (line_bytes + b"\n")


def _open_append_fd(log_path: Path) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    mode = 0o644
    return os.open(str(log_path), flags, mode)


def _lock_fd(fd: int) -> None:
    fcntl.flock(fd, fcntl.LOCK_EX)


def _write_all(fd: int, data: bytes, log_path: Path) -> None:
    n = os.write(fd, data)
    if n != len(data):
        raise RecorderIOError(
            f"Short write: wrote {n} of {len(data)} bytes to {log_path}"
        )


def _raise_mapped_os_error(e: OSError, log_path: Path) -> None:
    # ENOENT here effectively means parent dir missing (O_CREAT would create the file).
    if e.errno == errno.ENOENT:
        raise MissingSessionPath(
            f"Missing parent session directory: {log_path.parent}"
        ) from e
    raise RecorderIOError(f"{type(e).__name__}: {e}") from e


def _best_effort_close(fd: int | None) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        # Do not raise from finally (would mask real error)
        return


def _reject_embedded_newlines(data: bytes) -> None:
    # Allow exactly one trailing newline, but no other '\n' characters.
    core = data[:-1] if data.endswith(b"\n") else data
    if b"\n" in core:
        raise RecorderIOError(
            "Embedded newlines are not allowed in a single JSONL event"
        )
