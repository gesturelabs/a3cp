# tests/utils_helpers.py

import json
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = _REPO_ROOT / "schemas"


def load_example(module_name: str, kind: str) -> dict:
    """
    Load the latest example input/output JSON for a given module.
    :param module_name: e.g. "landmark_extractor"
    :param kind: "input" or "output"
    """
    path = SCHEMAS_DIR / module_name / f"{module_name}_{kind}_example.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing schema example: {path}")
    return json.loads(path.read_text())


def assert_valid_iso8601(timestamp: str):
    """
    Assert that a timestamp matches ISO 8601 format with UTC 'Z' suffix.
    Example: 2025-07-09T09:12:34.567Z
    """
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
    assert isinstance(timestamp, str), "Timestamp must be a string"
    assert re.match(pattern, timestamp), f"Invalid timestamp format: {timestamp}"
