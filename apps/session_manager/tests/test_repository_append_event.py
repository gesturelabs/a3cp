# apps/session_manager/tests/test_repository_append_event.py

import pathlib
import re


def test_session_manager_does_not_open_jsonl_files_directly() -> None:
    """
    Writer-boundary guardrail:
    No code under apps/session_manager/ may open/write *.jsonl directly.
    The only allowed recording path is schema_recorder.append_event().
    """
    root = pathlib.Path("apps/session_manager")
    assert root.exists()

    # Any occurrence of open()/Path.open() near ".jsonl" is a hard failure.
    patterns = [
        re.compile(r"open\([^)]*\.jsonl", re.IGNORECASE),
        re.compile(r"\.open\([^)]*\.jsonl", re.IGNORECASE),
        re.compile(r"Path\([^)]*\.jsonl", re.IGNORECASE),
        re.compile(r"\.write_text\(", re.IGNORECASE),
        re.compile(r"\.write_bytes\(", re.IGNORECASE),
    ]

    for py in root.rglob("*.py"):
        if "apps/session_manager/tests" in str(py):
            continue
        text = py.read_text(encoding="utf-8")
        for pat in patterns:
            assert not pat.search(
                text
            ), f"Direct JSONL/file write pattern found in {py}: {pat.pattern}"
