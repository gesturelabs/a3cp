from typing import Annotated, Dict, List, Literal

from pydantic import BaseModel, Field


class PartnerSpeechSegment(BaseModel):
    transcript: Annotated[str, Field(..., description="Raw transcribed partner speech")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of speech segment")
    ]
    language: Annotated[
        str, Field(..., description="BCP-47 language code (e.g., 'en', 'es')")
    ]


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


class SpeechContextClassifierInput(BaseModel):
    schema_version: Literal["1.0.1"] = Field(
        default="1.0.1", description="Schema version"
    )
    record_id: Annotated[
        str, Field(..., description="Unique ID for this inference request")
    ]
    user_id: Annotated[str, Field(..., description="User ID")]
    session_id: Annotated[str, Field(..., description="Session ID")]
    timestamp: Annotated[str, Field(..., description="UTC ISO8601 timestamp")]

    partner_speech: Annotated[
        List[PartnerSpeechSegment],
        Field(..., description="List of transcribed partner utterances"),
    ]

    vocabulary: Annotated[
        List[VocabularyItem],
        Field(..., description="User's gesture/vocalization intent mappings"),
    ]

    @staticmethod
    def example_input() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "rec_1234567890",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:56:00.000Z",
            "partner_speech": [
                {
                    "transcript": "Would you like to listen to a song or play a game now?",
                    "timestamp": "2025-07-14T17:55:58.000Z",
                    "language": "en",
                }
            ],
            "vocabulary": [
                {
                    "label": "play",
                    "modality": "gesture",
                    "examples": ["play", "game", "toys"],
                },
                {
                    "label": "music",
                    "modality": "vocalization",
                    "examples": ["sing", "music", "song"],
                },
                {
                    "label": "drink",
                    "modality": "gesture",
                    "examples": ["water", "juice", "drink"],
                },
                {
                    "label": "help",
                    "modality": "vocalization",
                    "examples": ["help", "assist", "support"],
                },
                {
                    "label": "toilet",
                    "modality": "gesture",
                    "examples": ["bathroom", "toilet", "pee"],
                },
            ],
        }


class SpeechContextClassifierOutput(BaseModel):
    schema_version: Literal["1.0.1"] = Field(
        default="1.0.1", description="Schema version"
    )
    record_id: Annotated[str, Field(..., description="Copied from input")]
    user_id: Annotated[str, Field(..., description="Copied from input")]
    session_id: Annotated[str, Field(..., description="Copied from input")]
    timestamp: Annotated[
        str, Field(..., description="UTC ISO8601 timestamp of prediction")
    ]

    matched_intents: Annotated[
        List[str],
        Field(..., description="List of relevant known intent labels matched"),
    ]

    relevance_scores: Annotated[
        Dict[str, float],
        Field(..., description="Confidence scores per matched intent"),
    ]

    flags: Annotated[
        Dict[str, bool],
        Field(
            ...,
            description="Optional boolean flags (e.g., partner_engaged, topic_shift)",
        ),
    ]

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "rec_1234567890",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:56:01.500Z",
            "matched_intents": ["music", "play"],
            "relevance_scores": {"music": 0.89, "play": 0.86},
            "flags": {"partner_engaged": True, "topic_shift": True},
        }
