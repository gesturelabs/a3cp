from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

import apps.schema_recorder.service as service_module
from apps.schema_recorder.repository import append_bytes
from apps.schema_recorder.service import MissingSessionPath, RecorderIOError
from schemas import A3CPMessage


def _utc_dt() -> datetime:
    return datetime(2025, 6, 15, 12, 34, 56, 789000, tzinfo=timezone.utc)


def _make_event_dict(*, user_id: str, session_id: str, source: str) -> dict:
    # Build as dict so we can safely add extra keys while keeping type-checkers happy.
    return {
        "schema_version": "1.0.1",
        "record_id": str(uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "source": source,
        "timestamp": _utc_dt(),
    }


def _make_event(
    *, user_id: str, session_id: str, source: str, extra_blob: str | None = None
) -> A3CPMessage:
    d = _make_event_dict(user_id=user_id, session_id=session_id, source=source)
    if extra_blob is not None:
        d["extra_blob"] = extra_blob  # allowed by A3CPMessage extra="allow"
    return A3CPMessage.model_validate(d)


def _envelope_bytes_for(message: A3CPMessage, recorded_at: str) -> bytes:
    envelope = {
        "recorded_at": recorded_at,
        "event": message.model_dump(mode="json"),
    }
    line = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")) + "\n"
    return line.encode("utf-8")


def test_near_limit_payload_appends_exactly_one_newline_terminated_jsonl_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange LOG_ROOT + required session directory (session_manager authority)
    log_root = tmp_path / "logs"
    session_dir = log_root / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("apps.schema_recorder.config.LOG_ROOT", log_root, raising=True)

    recorded_at = "2026-01-15T12:34:56.789Z"

    # Start with a message that includes an empty extra blob so the envelope shape is stable.
    msg = _make_event(user_id="u1", session_id="s1", source="tester", extra_blob="")

    base_len = len(_envelope_bytes_for(msg, recorded_at))

    # Keep a safety margin under the MAX to avoid off-by-a-few JSON overhead issues.
    target = service_module.MAX_EVENT_BYTES - 1024
    assert base_len < target, "Base event unexpectedly too large for near-limit test."

    fill_len = target - base_len
    msg2 = _make_event(
        user_id="u1",
        session_id="s1",
        source="tester",
        extra_blob="x" * fill_len,
    )

    # Act
    result = service_module.append_event(user_id="u1", session_id="s1", message=msg2)

    # Assert: file exists, exactly one line, newline-terminated, JSON parses
    log_path = log_root / "users" / "u1" / "sessions" / "s1.jsonl"
    assert log_path.exists()

    content = log_path.read_bytes()
    assert content.endswith(b"\n")
    lines = content.splitlines()
    assert len(lines) == 1

    obj = json.loads(lines[0].decode("utf-8"))
    assert set(obj.keys()) == {"recorded_at", "event"}
    assert obj["recorded_at"] == result.recorded_at
    assert obj["event"]["record_id"] == str(msg2.record_id)


def test_over_limit_raises_eventtoolarge_and_does_not_create_file_when_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_root = tmp_path / "logs"
    session_dir = log_root / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("apps.schema_recorder.config.LOG_ROOT", log_root, raising=True)

    # Definitely too large (service checks before repository IO)
    msg = _make_event(
        user_id="u1",
        session_id="s1",
        source="tester",
        extra_blob="x" * service_module.MAX_EVENT_BYTES,
    )

    log_path = log_root / "users" / "u1" / "sessions" / "s1.jsonl"
    assert not log_path.exists()

    with pytest.raises(service_module.EventTooLarge):
        service_module.append_event(user_id="u1", session_id="s1", message=msg)

    # Atomicity: file is not created
    assert not log_path.exists()


def test_over_limit_raises_eventtoolarge_and_does_not_change_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log_root = tmp_path / "logs"
    session_dir = log_root / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("apps.schema_recorder.config.LOG_ROOT", log_root, raising=True)

    log_path = log_root / "users" / "u1" / "sessions" / "s1.jsonl"
    log_path.write_text('{"preexisting":true}\n', encoding="utf-8")
    before = log_path.read_bytes()

    msg = _make_event(
        user_id="u1",
        session_id="s1",
        source="tester",
        extra_blob="x" * service_module.MAX_EVENT_BYTES,
    )

    with pytest.raises(service_module.EventTooLarge):
        service_module.append_event(user_id="u1", session_id="s1", message=msg)

    # Atomicity: file is unchanged
    after = log_path.read_bytes()
    assert after == before


def test_missing_parent_session_directory_raises_missing_session_path_and_creates_nothing(
    tmp_path: Path,
) -> None:
    # Parent dir intentionally not created
    log_root = tmp_path / "logs"
    log_path = log_root / "users" / "u1" / "sessions" / "s1.jsonl"
    assert not log_path.parent.exists()
    assert not log_path.exists()

    with pytest.raises(MissingSessionPath):
        append_bytes(log_path=log_path, line_bytes=b'{"ok":true}\n')

    # creates nothing
    assert not log_path.parent.exists()
    assert not log_path.exists()


def test_unwritable_directory_raises_recorder_io_error_and_creates_nothing(
    tmp_path: Path,
) -> None:
    # Create the parent session directory, but make it unwritable
    session_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Remove write permission from the directory (owner read/execute only)
    os.chmod(session_dir, 0o555)

    log_path = session_dir / "s1.jsonl"
    assert not log_path.exists()

    try:
        with pytest.raises(RecorderIOError):
            append_bytes(log_path=log_path, line_bytes=b'{"ok":true}\n')

        # File must not be created
        assert not log_path.exists()
    finally:
        # Restore permissions so pytest can clean up tmp_path
        os.chmod(session_dir, 0o755)


def test_unwritable_existing_file_raises_recorder_io_error_and_does_not_change_content(
    tmp_path: Path,
) -> None:
    session_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    log_path = session_dir / "s1.jsonl"
    log_path.write_bytes(b'{"preexisting":true}\n')
    before = log_path.read_bytes()

    # Make the file read-only; os.open(..., O_WRONLY|O_APPEND) should fail with EACCES
    os.chmod(log_path, 0o444)

    try:
        with pytest.raises(RecorderIOError):
            append_bytes(log_path=log_path, line_bytes=b'{"ok":true}\n')

        after = log_path.read_bytes()
        assert after == before
    finally:
        # Restore permissions for cleanup
        os.chmod(log_path, 0o644)


def test_concurrent_appends_are_not_interleaved_and_produce_valid_jsonl(
    tmp_path: Path,
) -> None:
    """
    Verifies that flock(LOCK_EX) prevents interleaved writes:

    - N concurrent append_bytes() calls
    - Exactly N newline-terminated lines appended
    - Each line parses as valid JSON
    """

    # Arrange
    session_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    log_path = session_dir / "s1.jsonl"

    N = 25
    errors: list[Exception] = []

    def worker(i: int) -> None:
        try:
            payload = {"i": i}
            line = json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"\n"
            append_bytes(log_path=log_path, line_bytes=line)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]

    # Act
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Assert: no worker raised
    assert not errors, f"Unexpected errors during concurrent appends: {errors}"

    # Assert: exactly N lines
    data = log_path.read_bytes()
    lines = data.splitlines()
    assert len(lines) == N

    # Assert: each line is valid JSON (no interleaving / corruption)
    seen = set()
    for raw in lines:
        obj = json.loads(raw.decode("utf-8"))
        assert "i" in obj
        seen.add(obj["i"])

    # Assert: all payloads accounted for (no lost or duplicated lines)
    assert seen == set(range(N))


def test_append_bytes_always_writes_one_newline_terminated_line(
    tmp_path: Path,
) -> None:
    session_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    log_path = session_dir / "s1.jsonl"

    # Caller forgets newline -> repository must ensure newline termination
    payload = {"ok": True}
    line = json.dumps(payload, separators=(",", ":")).encode("utf-8")  # no trailing \n

    append_bytes(log_path=log_path, line_bytes=line)

    data = log_path.read_bytes()
    assert data.endswith(b"\n")

    lines = data.splitlines()
    assert len(lines) == 1

    obj = json.loads(lines[0].decode("utf-8"))
    assert obj == payload


def test_append_bytes_rejects_embedded_newlines_and_creates_nothing(
    tmp_path: Path,
) -> None:
    session_dir = tmp_path / "logs" / "users" / "u1" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    log_path = session_dir / "s1.jsonl"
    assert not log_path.exists()

    # Two logical lines in one "append" is forbidden for JSONL integrity.
    bad = b'{"a":1}\n{"b":2}\n'

    with pytest.raises(RecorderIOError):
        append_bytes(log_path=log_path, line_bytes=bad)

    # Atomicity: must not create the file at all
    assert not log_path.exists()
