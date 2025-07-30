from typing import Annotated, List, Literal

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


class ClassifierRankingItem(BaseModel):
    intent: Annotated[str, Field(..., description="Matched intent label")]
    confidence: Annotated[
        float,
        Field(..., ge=0.0, le=1.0, description="Normalized confidence score"),
    ]


class SpeechContextClassifierInput(BaseModel):
    schema_version: Literal["1.0.1"] = Field(
        default="1.0.1", description="Schema version"
    )
    record_id: Annotated[
        str, Field(..., description="Unique ID for this inference request")
    ]
    user_id: Annotated[str, Field(..., description="Pseudonymous user ID")]
    session_id: Annotated[str, Field(..., description="Session ID")]
    timestamp: Annotated[str, Field(..., description="UTC ISO8601 timestamp")]

    partner_speech: Annotated[
        List[PartnerSpeechSegment],
        Field(..., description="List of transcribed partner utterances"),
    ]

    vocabulary: Annotated[
        List[VocabularyItem],
        Field(..., description="User’s intent vocabulary with examples"),
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


class ClassifierOutput(BaseModel):
    intent: Annotated[
        str | None,
        Field(..., description="Top matched intent label or null if no match"),
    ]
    confidence: Annotated[
        float,
        Field(..., ge=0.0, le=1.0, description="Confidence score for top intent"),
    ]
    ranking: Annotated[
        List[ClassifierRankingItem],
        Field(..., description="Ordered list of matched intents with confidence"),
    ]
    language_used: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional BCP-47 language code used for LLM prompt",
        ),
    ]
    prompt_version: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional identifier for LLM prompt template",
        ),
    ]


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
    modality: Literal["speech"] = Field(
        default="speech", description="Modality of source input"
    )
    source: Literal["caregiver"] = Field(
        default="caregiver", description="Who produced the speech input"
    )
    classifier_output: Annotated[
        ClassifierOutput,
        Field(..., description="Inference result for partner speech intent mapping"),
    ]

    @staticmethod
    def example_output() -> dict:
        return {
            "schema_version": "1.0.1",
            "record_id": "rec_1234567890",
            "user_id": "elias01",
            "session_id": "sess_20250714_e01",
            "timestamp": "2025-07-14T17:56:01.500Z",
            "modality": "speech",
            "source": "caregiver",
            "classifier_output": {
                "intent": "music",
                "confidence": 0.89,
                "ranking": [
                    {"intent": "music", "confidence": 0.89},
                    {"intent": "play", "confidence": 0.86},
                ],
                "language_used": "en",
                "prompt_version": "v2.1_en_semantic_vocabulary",
            },
        }
