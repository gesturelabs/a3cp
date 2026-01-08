import pytest


@pytest.fixture(autouse=True)
def _force_log_root_tmp(tmp_path, monkeypatch):
    """
    Prevent any test (anywhere in the repo) from writing to ./logs.
    Forces LOG_ROOT into pytest temp dirs.
    """
    monkeypatch.setenv("LOG_ROOT", str(tmp_path / "logs"))
