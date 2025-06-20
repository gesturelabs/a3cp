# schemas/raw_action_record.py

from datetime import datetime
from typing import Annotated, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

INTERFACE_SCHEMA_PATH = "interfaces/raw_action_record.schema.json"


class RawActionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Disallow undeclared fields

    schema_version: Annotated[str, Field(default="1.0", frozen=True)]
    record_id: Annotated[UUID, Field()]
    user_id: Annotated[str, Field()]
    session_id: Annotated[str, Field()]
    timestamp: Annotated[datetime, Field()]

    stream_segment_id: Annotated[Optional[str], Field(default=None)]
    sequence_id: Annotated[Optional[str], Field(default=None)]
    frame_index: Annotated[Optional[int], Field(default=None)]

    modality: Annotated[str, Field()]
    source: Annotated[str, Field()]
    device_id: Annotated[Optional[str], Field(default=None)]
    is_demo: Annotated[Optional[bool], Field(default=None)]
    consent_given: Annotated[Optional[bool], Field(default=None)]

    context_location: Annotated[Optional[str], Field(default=None)]
    context_prompt_type: Annotated[Optional[str], Field(default=None)]
    context_partner_utterance: Annotated[Optional[str], Field(default=None)]
    context_session_notes: Annotated[Optional[str], Field(default=None)]
    context_topic_tag: Annotated[Optional[str], Field(default=None)]
    context_relevance_score: Annotated[Optional[float], Field(default=None)]
    context_flags: Annotated[Optional[Dict[str, bool]], Field(default=None)]

    intent_label: Annotated[Optional[str], Field(default=None)]
    label_status: Annotated[Optional[str], Field(default=None)]
    classifier_output: Annotated[Optional[Dict[str, float]], Field(default=None)]
    label_correction: Annotated[Optional[str], Field(default=None)]

    final_decision: Annotated[Optional[str], Field(default=None)]
    output_type: Annotated[Optional[str], Field(default=None)]
    output_phrase: Annotated[Optional[str], Field(default=None)]
    output_mode: Annotated[Optional[str], Field(default=None)]

    vector_version: Annotated[Optional[str], Field(default=None)]
    raw_features_ref: Annotated[Optional[Dict[str, str]], Field(default=None)]

    memory_intent_boosts: Annotated[Optional[Dict[str, float]], Field(default=None)]
    memory_fallback_suggestions: Annotated[Optional[List[str]], Field(default=None)]
    memory_hint_used: Annotated[Optional[bool], Field(default=None)]

    ASR_confidence_score: Annotated[Optional[float], Field(default=None)]
