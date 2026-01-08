# schema_recorder Pydantic model
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RecorderConfig(BaseModel):
    log_format: Literal["jsonl", "npz"] = Field(
        "jsonl", description="Log format for recorded schema data"
    )
    log_dir: Path = Field(
        ..., description="Directory to write logs to (e.g., logs/users/)"
    )
    enable_hashing: bool = Field(
        default=True, description="Whether to hash each record for audit trace"
    )
    max_file_size_mb: Optional[int] = Field(
        None, description="Optional log rotation size in megabytes"
    )
    allow_schema_override: bool = Field(
        default=False, description="Allow caller to override inferred schema name"
    )

    @staticmethod
    def example_input() -> dict:
        return {
            "log_format": "jsonl",
            "log_dir": "./logs",
            "enable_hashing": True,
            "max_file_size_mb": 100,
            "allow_schema_override": False,
        }

    @staticmethod
    def example_output() -> dict:
        # Recorder config is usually not used for output
        return RecorderConfig.example_input()
