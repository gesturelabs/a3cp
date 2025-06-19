# SCHEMA_OVERVIEW.md

> ⚠️ This document is a human-readable summary of the canonical schema.  
> The authoritative version is defined in `schemas/` and validated at runtime.

---

## Core Metadata

| Field Name       | Type     | Req | Description                                         | Example                                 |
|------------------|----------|-----|-----------------------------------------------------|-----------------------------------------|
| schema_version   | string   | ✅  | Semantic schema version                             | "1.0.0"                                 |
| record_id        | UUID     | ✅  | Unique ID for this record                           | "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56"  |
| user_id          | string   | ✅  | Pseudonymous user identifier                        | "elias01"                               |
| session_id       | string   | ✅  | Logical session grouping ID                         | "a3cp_sess_2025-06-15_elias01"          |
| timestamp        | datetime | ✅  | ISO 8601 UTC timestamp with milliseconds            | "2025-06-15T12:34:56.789Z"              |

---

## Stream Structure

| Field Name         | Type     | Req | Description                                           | Example                      |
|--------------------|----------|-----|-------------------------------------------------------|------------------------------|
| stream_segment_id  | string   | ❌  | Optional segment/window ID                            | "elias01_2025-05-05T12:31:45Z" |
| sequence_id        | string   | ❌  | Input frame/utterance sequence ID                     | "elias01_000023"             |
| frame_index        | integer  | ❌  | Index of this frame in the sequence                   | 23                           |

---

## Input Metadata

| Field Name      | Type    | Req | Description                                        | Example             |
|-----------------|---------|-----|----------------------------------------------------|---------------------|
| modality        | string  | ✅  | Input type: "gesture", "audio", "speech"           | "gesture"           |
| source          | string  | ✅  | Who produced input: "communicator", "caregiver"    | "communicator"      |
| device_id       | string  | ❌  | Device ID for the hardware capturing input         | "jetson_nano_01"    |
| is_demo         | boolean | ❌  | Whether this record is from a demo or test session | false               |
| consent_given   | boolean | ❌  | Whether informed consent was obtained              | true                |

---

## Contextual Tags

| Field Name                  | Type     | Req | Description                                             | Example                    |
|-----------------------------|----------|-----|---------------------------------------------------------|----------------------------|
| context_location            | string   | ❌  | Coarse-grained location or room label                   | "kitchen"                  |
| context_prompt_type         | string   | ❌  | Type of prompting: "prompted", "spontaneous", "other"   | "spontaneous"              |
| context_partner_utterance   | string   | ❌  | Partner or caregiver utterance                          | "Are you hungry?"          |
| context_session_notes       | string   | ❌  | Freeform caregiver/environment notes                    | "User distracted by noise" |
| context_topic_tag           | string   | ❌  | NLP-inferred topic tag                                  | "food"                     |
| context_relevance_score     | float    | ❌  | Score of relevance to expected intents                  | 0.87                       |
| context_flags               | object   | ❌  | Flags such as {"question_detected": true}               | {"question_detected": true}|

---

## User & Classifier Labels

| Field Name         | Type     | Req | Description                                        | Example                               |
|--------------------|----------|-----|----------------------------------------------------|---------------------------------------|
| intent_label       | string   | ❌  | Initial label from user or annotator              | "help"                                |
| label_status       | string   | ❌  | "unconfirmed", "confirmed", "corrected"           | "unconfirmed"                         |
| classifier_output  | object   | ❌  | Model prediction and confidence                   | {"intent": "eat", "confidence": 0.91} |
| label_correction   | string   | ❌  | Caregiver-provided correction                     | "drink"                               |

---

## CARE Final Output

| Field Name       | Type    | Req | Description                                        | Example           |
|------------------|---------|-----|----------------------------------------------------|-------------------|
| final_decision   | string  | ❌  | Final resolved decision after clarification        | "eat"             |
| output_type      | string  | ❌  | One of: "intent", "clarification", "none"          | "intent"          |
| output_phrase    | string  | ❌  | Phrase rendered in AAC output                      | "I want to eat"   |
| output_mode      | string  | ❌  | AAC output mode: "speech", "text", "symbol"        | "speech"          |

---

## Vector & Feature Metadata

| Field Name        | Type     | Req | Description                                            | Example        |
|-------------------|----------|-----|--------------------------------------------------------|----------------|
| vector_version    | string   | ❌  | Version of encoder used for feature extraction         | "v2.1"         |
| raw_features_ref  | object   | ❌  | Object containing pointer and metadata for external vector | see below  |

Example `raw_features_ref`:

```json
{
  "uri": "/data/elias01/gesture_000023.parquet",
  "hash": "sha256:abcdef1234567890...",
  "encoding": "landmark_v2.1",
  "dims": 128,
  "format": "parquet"
}

## Memory-Based Hints

| Field Name                  | Type     | Req | Description                                      | Example                             |
|----------------------------|----------|-----|--------------------------------------------------|-------------------------------------|
| memory_intent_boosts       | object   | ❌  | Intent weighting from user history               | {"eat": 0.15, "play": 0.05}         |
| memory_fallback_suggestions| list     | ❌  | Backup intents from memory                       | ["rest", "drink", "eat"]            |
| memory_hint_used           | boolean  | ❌  | Whether memory influenced the current output     | true                                |

---

## Other Fields

| Field Name            | Type   | Req | Description                                  | Example |
|-----------------------|--------|-----|----------------------------------------------|---------|
| ASR_confidence_score  | float  | ❌  | Confidence score from speech transcription   | 0.92    |

---

**Note:** All optional fields should be omitted if not applicable.  
All fields are flat (no dot notation) for compatibility with JSONL and flat log systems.
