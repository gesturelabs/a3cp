# tests/utils/test_paths.py
from pathlib import Path

from utils.paths import session_log_path


def test_session_log_path_is_pure_and_deterministic(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"  # intentionally does NOT exist

    p1 = session_log_path(log_root=log_root, user_id="u123", session_id="sess_abc")
    p2 = session_log_path(log_root=log_root, user_id="u123", session_id="sess_abc")

    assert p1 == p2
    assert str(p1).endswith("/logs/users/u123/sessions/sess_abc.jsonl") or str(
        p1
    ).endswith("\\logs\\users\\u123\\sessions\\sess_abc.jsonl")

    # Purity check: function must not create directories or files.
    assert not log_root.exists()
    assert not p1.exists()
