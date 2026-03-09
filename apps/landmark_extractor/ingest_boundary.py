from __future__ import annotations

from typing import Any, List

from pydantic import TypeAdapter

from schemas import (
    LandmarkExtractorFrameInput,
    LandmarkExtractorInput,
    LandmarkExtractorTerminalInput,
)

_ingest_adapter = TypeAdapter(LandmarkExtractorInput)

INGEST_SINK: List[LandmarkExtractorFrameInput | LandmarkExtractorTerminalInput] = []


async def ingest(msg: Any) -> None:
    validated = _ingest_adapter.validate_python(msg)
    INGEST_SINK.append(validated)
