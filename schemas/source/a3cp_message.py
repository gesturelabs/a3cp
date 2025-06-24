from datetime import datetime
from typing import Annotated, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

INTERFACE_SCHEMA_PATH = "interfaces/a3cp_message.schema.json"


class A3CPMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Core Metadata
    schema_version: Annotated[str, Field(default="1.0.0", frozen=True)]
    record_id: Annotated[UUID, Field()]
    user_id: Annotated[str, Field()]
    session_id: Annotated[str, Field()]
    timestamp: Annotated[datetime, Field()]
    modality: Annotated[str, Field()]
    source: Annotated[str, Field()]

    # Input & Stream Fields
    stream_segment_id: Annotated[Optional[str], Field(default=None)]
    sequence_id: Annotated[Optional[str], Field(default=None)]
    frame_index: Annotated[Optional[int], Field(default=None)]
    device_id: Annotated[Optional[str], Field(default=None)]
    is_demo: Annotated[Optional[bool], Field(default=None)]
    consent_given: Annotated[Optional[bool], Field(default=None)]

    # Contextual Tags
    context_location: Annotated[Optional[str], Field(default=None)]
    context_prompt_type: Annotated[Optional[str], Field(default=None)]
    context_partner_speech: Annotated[Optional[str], Field(default=None)]
    context_session_notes: Annotated[Optional[str], Field(default=None)]
    context_topic_tag: Annotated[Optional[str], Field(default=None)]
    context_relevance_score: Annotated[Optional[float], Field(default=None)]
    context_flags: Annotated[Optional[Dict[str, bool]], Field(default=None)]

    # Classifier Output & Feedback
    intent_label: Annotated[Optional[str], Field(default=None)]
    label_status: Annotated[Optional[str], Field(default=None)]
    classifier_output: Annotated[Optional[Dict[str, float]], Field(default=None)]
    label_correction: Annotated[Optional[str], Field(default=None)]
    final_decision: Annotated[Optional[str], Field(default=None)]
    output_type: Annotated[Optional[str], Field(default=None)]

    # AAC Output Fields
    output_phrase: Annotated[Optional[str], Field(default=None)]
    output_mode: Annotated[Optional[str], Field(default=None)]

    # Vector & Feature Metadata
    vector_version: Annotated[Optional[str], Field(default=None)]
    raw_features_ref: Annotated[Optional[Dict[str, str]], Field(default=None)]

    # Memory-Based Output
    memory_intent_boosts: Annotated[Optional[Dict[str, float]], Field(default=None)]
    memory_fallback_suggestions: Annotated[Optional[List[str]], Field(default=None)]
    memory_hint_used: Annotated[Optional[bool], Field(default=None)]

    # Additional Confidence Signal
    asr_confidence_score: Annotated[
        Optional[float], Field(default=None, alias="ASR_confidence_score")
    ]
