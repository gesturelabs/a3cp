from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from apps.landmark_extractor import service
from schemas import LandmarkExtractorInput

_ingest_adapter = TypeAdapter(LandmarkExtractorInput)


async def ingest(msg: Any) -> None:
    validated = _ingest_adapter.validate_python(msg)
    await service.handle_message(validated)
