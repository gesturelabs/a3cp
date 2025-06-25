# speech_context_infererer Pydantic model

from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# -------------------------
# PartnerSpeechSegment: single transcript chunk from partner
# -------------------------
class PartnerSpeechSegment(BaseModel):
    transcript: Annotated[str, Field(..., description="Raw transcribed partner speech")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of speech segment")
    ]
    language: Annotated[
        str, Field(..., description="BCP-47 language code (e.g., 'en', 'es')")
    ]


# -------------------------
# VocabularyItem: user-trained label for gesture or vocalization
# -------------------------
class VocabularyItem(BaseModel):
    label: Annotated[
        str,
        Field(..., description="Intent label trained by user (e.g., 'help', 'drink')"),
    ]
    modality: Annotated[
        Literal["gesture", "vocalization"],
        Field(..., description="Modality of expression"),
    ]
    examples: Annotated[
        List[str],
        Field(..., description="Example words or phrases mapped to this intent"),
    ]


# -------------------------
# SpeechContextInfererInput: input structure
# -------------------------
class SpeechContextInfererInput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(default="1.0.0", frozen=True)

    # Metadata
    record_id: Annotated[
        str, Field(..., description="Unique ID for this inference request")
    ]
    user_id: Annotated[str, Field(..., description="User ID")]
    session_id: Annotated[str, Field(..., description="Session ID")]
    timestamp: Annotated[str, Field(..., description="UTC ISO8601 timestamp")]

    # Transcript and history
    partner_speech: Annotated[
        List[PartnerSpeechSegment],
        Field(..., description="List of transcribed partner utterances"),
    ]

    # Known user vocabulary
    vocabulary: Annotated[
        List[VocabularyItem],
        Field(..., description="User's gesture/vocalization intent mappings"),
    ]


# -------------------------
# SpeechContextInfererOutput: inference result
# -------------------------
class SpeechContextInfererOutput(BaseModel):
    schema_version: Literal["1.0.0"] = Field(default="1.0.0", frozen=True)

    record_id: Annotated[str, Field(..., description="Copied from input")]
    user_id: Annotated[str, Field(..., description="Copied from input")]
    session_id: Annotated[str, Field(..., description="Copied from input")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of prediction")
    ]

    prompt_type: Annotated[
        Optional[Literal["question", "command", "unknown"]],
        Field(..., description="Type of communicative prompt inferred"),
    ]
    topic: Annotated[
        Optional[str],
        Field(
            ..., description="High-level topic category (e.g., 'food', 'navigation')"
        ),
    ]

    matched_intents: Annotated[
        List[str],
        Field(..., description="List of relevant known intent labels matched"),
    ]
    relevance_scores: Annotated[
        Dict[str, float], Field(..., description="Confidence scores per matched intent")
    ]
    flags: Annotated[
        Dict[str, bool],
        Field(
            ..., description="Boolean flags (e.g., is_question, needs_clarification)"
        ),
    ]

    # Optional fallback
    needs_clarification: Annotated[
        bool, Field(..., description="True if no matches found or low relevance")
    ]
