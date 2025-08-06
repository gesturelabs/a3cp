# SCHEMA_REFERENCE.md
v 1.1

This document defines the canonical runtime data schema used across all A3CP modules for internal communication and logging. The schema is represented as a `pydantic` model (`A3CPMessage`) under `schemas/a3cp_message.py` and is mirrored in `interfaces/a3cp_message.schema.json`.

Each field is documented with its type, version history, required status, typical usage, and which modules produce or consume it.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Metadata Fields](#core-metadata-fields)
3. [Input & Stream Fields](#input--stream-fields)
4. [Contextual Tags](#contextual-tags)
5. [Classifier Output](#classifier-output)
6. [Clarification & Feedback](#clarification--feedback)
7. [Memory-Based Output](#memory-based-output)
8. [Vector & Feature Metadata](#vector--feature-metadata)
9. [AAC Output Fields](#aac-output-fields)
10. [Schema Versioning & Field History](#schema-versioning--field-history)
11. [Module Usage Matrix](#module-usage-matrix)

---

## 1. Overview

All internal communication in A3CP uses a canonical structure: A3CPMessage.

Each message is:
- Serialized as JSON
- Validated at runtime using Pydantic
- Exported as JSON Schema to interfaces/
- Logged as .jsonl under logs/users/ and logs/sessions/

The schema enables consistent interoperability across modules handling:
- Multimodal input (gesture, speech, audio, image)
- Classifier inference and confidence scoring
- Clarification, memory-based adjustment, and AAC output

Messages are versioned (schema_version), traceable (record_id), and grouped by session (session_id).
All modules must validate schema_version and handle optional fields gracefully.



---
## 2. Core Metadata Fields


These fields are required in every `A3CPMessage`. They provide version control,
traceability, session grouping, modality tagging, and audit timestamps.

All timestamps must use ISO 8601 format with millisecond precision and a "Z" suffix.

+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+
| Field          | Type           | Req | Example                                      | Description                                                   |
+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+
| schema_version | str            | ✅  | "1.0.0"                                      | Semantic version of the schema (MAJOR.MINOR.PATCH)            |
| record_id      | UUID           | ✅  | "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56"       | Unique ID for this message (UUIDv4, assigned at creation)     |
| user_id        | str            | ✅  | "elias01"                                    | Pseudonymous user identifier                                  |
| session_id     | str            | ❌  | "a3cp_sess_2025-06-15_elias01"               | Assigned by session_manager to group related inputs           |
| timestamp      | datetime       | ✅  | "2025-06-15T12:34:56.789Z"                   | ISO 8601 UTC timestamp with milliseconds and "Z" suffix       |
| modality       | Literal[str]   | ❌  | "gesture"                                    | Assigned by classifier; one of: "gesture", "audio", etc.      |
| source         | str            | ❌  | "gesture_classifier"                         | Name of the module emitting this message                      |
| performer_id   | str            | ✅* | "carer01"                                    | Actor performing input; required for human input messages; "system" for system-generated. |
+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+

(*) performer_id is required for all human-originated inputs. For system-generated messages, it may be set to "system" or omitted with validation.

Notes:
- record_id uniquely identifies a single message instance and must be a UUIDv4. It is immutable once assigned.
- session_id groups multiple related messages within the same interaction window and is assigned by the session_manager.
- schema_version must be present in all records and follow strict Semantic Versioning (MAJOR.MINOR.PATCH).
- modality indicates the input type and must use a controlled vocabulary; it is assigned by classifier modules.
- source identifies the module emitting the message and must be a string corresponding to a module name; no fixed enumeration applies.
- performer_id identifies the actor performing the input and is required for all human-originated inputs; system-generated messages may use "system" or omit this field.
- All timestamps must be in UTC with millisecond precision and include the "Z" suffix.
- modality should be treated as an enum to prevent invalid values.

Allowed Values:
- modality: one of "gesture", "audio", "speech", "image", "multimodal"
- source: string corresponding to the name of the emitting module (e.g., "gesture_classifier", "session_manager"). No fixed set; must be consistent within system.
- performer_id: string pseudonymous identifier (e.g., "user123", "carer01"), or the special value "system" for system-generated messages.


## Section 3: Input & Stream Fields

This section defines fields related to raw input capture, temporal ordering,
stream segmentation, and device-level metadata.

These fields are primarily used by modules such as:
- Streamers
- Sensor workers (e.g., camera/audio feed)
- Logging and schema recording components

### 3.1 Temporal Structure & Stream Windowing

These fields describe when and how the input was captured, and optionally place
it within a structured sequence or stream segment. Used for aligning multi-frame
inputs such as audio, video, or skeletal streams.

+---------------------+----------+-----+--------------------------------------------+-------------------------------------------------------------+
| Field Name          | Type     | Req | Example                                    | Description                                                 |
+---------------------+----------+-----+--------------------------------------------+-------------------------------------------------------------+
| timestamp           | datetime | ✅  | "2025-05-05T12:31:46.123Z"                 | ISO 8601 UTC timestamp of when the input was captured       |
| stream_segment_id   | str      | ❌  | "elias01_2025-05-05T12:31:45Z"             | Optional ID grouping frames into a stream segment           |
| sequence_id         | str      | ❌  | "elias01_000023"                           | Optional global identifier for this input frame or utterance|
| frame_index         | int      | ❌  | 23                                         | Index of this frame within the segment or sequence          |
+---------------------+----------+-----+--------------------------------------------+-------------------------------------------------------------+

Notes:
- If `sequence_id` is present, it must be unique within the session.
- `frame_index` is used for aligning dense input streams (e.g., video frames,
  audio windows, skeletal keypoints).

---

### 3.2 Input Signal Metadata

+------------+----------+-----+------------------------+------------------------------------------------------------------------------+
| Field Name | Type     | Req | Example                | Description                                                                  |
+------------+----------+-----+------------------------+------------------------------------------------------------------------------+
| modality   | Literal[str] | ❌ | "gesture"              | Type of input; assigned by classifier modules. One of: "gesture", "audio", "speech", "image", "multimodal".              |
| source     | str      | ❌  | "gesture_classifier"    | Name of the module emitting the message (e.g., "gesture_classifier", "session_manager"). Not fixed vocabulary.           |
| device_id  | str      | ❌  | "jetson_nano_01"        | Hardware identifier of the capture device.                                   |
| is_demo    | bool     | ❌  | false                  | Whether this is a synthetic/test/demo sample.                                |
| consent_given | bool  | ❌  | true                   | Indicates whether informed consent was captured for this input.              |
+------------+----------+-----+------------------------+------------------------------------------------------------------------------+

Notes:
- `modality` is optional in initial inputs and required in classifier outputs.
- `source` identifies the module emitting the message, supporting traceability.
- `device_id`, `is_demo`, and `consent_given` are optional flags for metadata and ethics compliance.

---

### 3.3 Vector Encoding & Feature Extraction

+--------------------+----------+-----+-----------------------------+-------------------------------------------------------------------------+-----------+
| Field Name         | Type     | Req | Example                     | Description                                                             | Version   |
+--------------------+----------+-----+-----------------------------+-------------------------------------------------------------------------+-----------+
| vector_version     | string   | ❌  | "v2.1"                      | Version of the vector encoder used to produce features.                 | v1.0      |
| raw_features_ref   | object   | ❌  | See schema below            | Reference to external vector file or array.                             | v1.0      |
+--------------------+----------+-----+-----------------------------+-------------------------------------------------------------------------+-----------+

#### raw_features_ref schema

{
  "uri": "/data/elias01/gesture_000023.parquet",
  "hash": "sha256:abcdef1234567890...",
  "encoding": "landmark_v2.1",
  "dims": 128,
  "format": "parquet"
}

+------------+----------+-----+-------------------------------------------------------------------------+
| Subfield   | Type     | Req | Description                                                             |
+------------+----------+-----+-------------------------------------------------------------------------+
| uri        | string   | ✅  | Path or URI to vector file (e.g., ".parquet", ".npz", or ".npy").       |
| hash       | string   | ✅  | Content hash (e.g., SHA-256) of the vector file for integrity checking. |
| encoding   | string   | ✅  | Name and version of the encoder used (e.g., "landmark_v2.1").           |
| dims       | integer  | ✅  | Dimensionality of the vector.                                           |
| format     | string   | ✅  | File format of the stored vector (e.g., "parquet", "npy", "npz").       |
+------------+----------+-----+-------------------------------------------------------------------------+

Notes:
- The 'vector' field (inline float list) is deprecated and should be used only for unit tests with vectors fewer than 5 elements.
- All production logs MUST reference external vectors via 'raw_features_ref' with a verified integrity hash.
- Future schema versions may require 'vector_version' to match or be consistent with 'raw_features_ref.encoding'.






## 4. Contextual Tags

This section defines optional fields that situate the input within its surrounding physical, social, or interactional environment. These fields are particularly important for disambiguating intent, modeling behavioral patterns, and providing priors to downstream modules such as the CARE Engine or Clarification Planner.

All fields in this section are optional but strongly encouraged when available.

---

### 4.1 Prompt & Environment Context

These fields are grouped under the `context` object.

| Field Name               | Type     | Req | Example                    | Description                                                                 |
|--------------------------|----------|-----|----------------------------|-----------------------------------------------------------------------------|
| `context_location`       | string   | ❌  | `"kitchen"`                | Coarse location or room tag.                                                |
| `context_prompt_type`    | string   | ❌  | `"natural_use"`            | One of: `"prompted"`, `"natural_use"`, `"other"`.                          |
| `context_partner_speech`| string   | ❌  | `"Are you hungry?"`        | Verbatim or paraphrased caregiver/partner utterance preceding the action.  |
| `context_session_notes` | string   | ❌  | `"User distracted by noise"` | Freeform caregiver notes or environment annotations.                     |

---

### 4.2 Derived Context Tags _(planned for future versions)_

These fields are typically computed post-recording by NLP or memory subsystems. They are optional and **not yet active in schema version 1.0.0**.

| Field Name                | Type           | Req | Example                         | Description                                                                |
|---------------------------|----------------|-----|----------------------------------|----------------------------------------------------------------------------|
| `context_topic_tag`       | string         | ❌  | `"food"`                         | Inferred topic derived from partner speech or other cues.                  |
| `context_relevance_score` | float          | ❌  | `0.87`                           | Confidence score for relevance to expected/known intents.                  |
| `context_flags`           | object          | ❌  | `{ "question_detected": true }`  | Map of boolean context flags. See below.                                   |

#### `context.flags` may include:

- `"question_detected"`: Was the partner speech a question?
- `"ambiguous_intent"`: Did the user action appear ambiguous?
- `"requires_attention"`: Did the caregiver manually flag the situation?

**Notes:**
- These derived tags help support clarification workflows, scaffolding triggers, and interpretability layers.
- `context` should be implemented as a **nested object** in both schema and serialized JSON (not flat dot notation).

## 5 Classifier Output & Label Fields

This section captures intent predictions and label provenance from multiple modalities,
their human annotations, and final clarifications. It covers evolving interpretations
from initial AI classification through human/caregiver correction to final resolved output.

Used by: Classifier modules, Input Broker, Clarification Planner, Feedback Logger, CARE Engine

---

### 5.1. classifier_output_components

Per-modality AI predictions contributing to the final decision.

+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+
| Field Name                   | Type   | Req | Example                    | Description                                                  |
+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+
| classifier_output_components | dict   | ❌  | See subfields              | Per-modality predictions keyed by modality (e.g., "gesture") |
+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+

Each modality entry contains:

+------------+-----------+-----+----------------------------+-------------------------------------------------------------+
| Subfield   | Type      | Req | Example                    | Description                                                 |
+------------+-----------+-----+----------------------------+-------------------------------------------------------------+
| intent     | string    | ✅  | "I love you"               | Predicted intent label from this modality                   |
| confidence | float     | ✅  | 0.82                       | Confidence score between 0.0 and 1.0                        |
| timestamp  | datetime  | ❌  | "2025-07-31T10:15:01.123Z" | When the classifier generated this prediction               |
+------------+-----------+-----+----------------------------+-------------------------------------------------------------+

Notes:
- Only modalities present should be included.
- This structure supplements but does not replace the final `intent` field.

---

### 2. classifier_output

AI model inference summary.

+---------------------+--------+-----+-------------------------------------------+-------------------------------------------------------------+
| Field Name          | Type   | Req | Example                                   | Description                                                 |
+---------------------+--------+-----+-------------------------------------------+-------------------------------------------------------------+
| classifier_output   | object | ❌  | { "intent": "eat", "confidence": 0.91 }  | Aggregate model output; keys may include `intent`, `confidence`, `ranking`, `model_version`, `timestamp` |
+---------------------+--------+-----+-------------------------------------------+-------------------------------------------------------------+



## 6. Clarification & Feedback

This section captures the system’s capacity to detect ambiguity (clarification), refine or override intent classification (label_correction), and finalize communicative output (final_decision). It includes structured metadata for triggering clarification, human intervention, and outcome tracking.

All fields are optional unless required by a specific module (e.g., feedback logger or session manager).

---

### 6.1 Label Status & Corrections

+--------------------+---------+-----+------------------+-------------------------------------------------------------+
| Field Name         | Type    | Req | Example          | Description                                                 |
+--------------------+---------+-----+------------------+-------------------------------------------------------------+
| label_status       | string  | ❌  | "confirmed"      | Label trust status. One of: "unconfirmed", "confirmed", "corrected". |
| label_correction   | string  | ❌  | "drink"          | Human override of the model or user label, applied post-inference.    |
+--------------------+---------+-----+------------------+-------------------------------------------------------------+

Allowed values for label_status:
- "unconfirmed": Initial annotation without verification
- "confirmed": Human-reviewed or validated
- "corrected": Model label has been overridden

Note: Only trusted sources (e.g., caregivers, expert annotators) should populate label_correction.

---

### 6.2 Consent and Demonstration Flags

+----------------+---------+-----+---------+-------------------------------------------------------------+
| Field Name     | Type    | Req | Example | Description                                                 |
+----------------+---------+-----+---------+-------------------------------------------------------------+
| consent_given  | boolean | ❌  | true    | Whether explicit informed consent was obtained for this input.|
| is_demo        | boolean | ❌  | false   | Whether this record is synthetic or for demonstration purposes only. |
+----------------+---------+-----+---------+-------------------------------------------------------------+

Use: These flags support ethics compliance, audit filtering, and exclusion from training pipelines.

---

### 6.3 Final Decision & Output Mode

+------------------+---------+-----+-----------+-------------------------------------------------------------+
| Field Name       | Type    | Req | Example   | Description                                                 |
+------------------+---------+-----+-----------+-------------------------------------------------------------+
| final_decision   | string  | ❌  | "eat"     | Final resolved intent after feedback, override, or clarification. |
| output_type     | string  | ❌  | "intent"  | Output category. One of: "intent", "clarification", "none".  |
+------------------+---------+-----+-----------+-------------------------------------------------------------+

Allowed values for output_type:
- "intent": Final user intent has been resolved
- "clarification": Follow-up or request for disambiguation
- "none": No output generated (e.g., inconclusive input)

Warning:
Do not pre-populate final_decision or output_type before resolution is complete. These fields represent post-clarification outcomes and must be kept distinct from initial predictions.

---

### 6.4 Clarification Metadata

All clarification planning metadata is grouped under the optional `clarification` object. This object is typically written by the `clarification_planner` and read by downstream modules such as the `llm_clarifier`, `feedback_log`, or `memory_interface`.

+------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+
| Field                        | Type             | Req | Example                          | Description                                                  |
+------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+
| clarification.needed         | boolean          | ✅  | true                             | Whether clarification should be initiated for this input.   |
| clarification.reason         | string           | ❌  | "low_confidence"                 | Explanation for triggering clarification.                   |
| clarification.candidates     | list of strings  | ❌  | ["eat", "drink"]                 | Top ambiguous or tied intent predictions.                   |
| clarification.confidence_scores | list of floats  | ❌  | [0.38, 0.36]                    | Confidence values aligned with candidates.                  |
| clarification.threshold_used | float            | ❌  | 0.40                            | Threshold that triggered the clarification logic.           |
+------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+


Notes:
- All fields are optional except clarification.needed.
- If clarification.needed is false, this object may be omitted entirely.
- clarification.* fields are advisory metadata for interaction planning, not intent resolution.


## 7. Memory-Based Output

This section contains optional fields populated by the CARE Engine’s memory modules. These fields trace whether past interactions, frequency counts, or adaptive user weights influenced the decision pipeline.

All fields below are part of the optional `memory` object and only appear when memory was queried.

---

### 7.1 User-Specific Boosts

| Field Name       | Type              | Req | Example                          | Description                                                                 |
|------------------|-------------------|-----|----------------------------------|-----------------------------------------------------------------------------|
| `intent_boosts`  | Dict[str, float]  | ❌  | `{ "eat": 0.15, "play": 0.05 }`  | Per-user intent likelihood boosts based on prior interaction history.      |

Used by CARE Engine’s confidence evaluator or fusion planner to adjust ranking of classifier outputs. Should not be interpreted as ground truth.

---

### 7.2 Fallback Suggestions

| Field Name            | Type     | Req | Example                      | Description                                                                      |
|-----------------------|----------|-----|------------------------------|----------------------------------------------------------------------------------|
| `fallback_suggestions`| list     | ❌  | `["rest", "drink", "eat"]`  | Ranked list of intents from memory, shown when classifier confidence is low.     |

Suggestions should be **ordered by descending estimated relevance** and may be presented to caregivers for manual selection.

---

### 7.3 Hint Usage Flag

| Field Name     | Type    | Req | Example | Description                                                                 |
|----------------|---------|-----|---------|-----------------------------------------------------------------------------|
| `hint_used`    | boolean | ❌  | `true`  | Indicates whether memory-based hints contributed to the final decision.     |

Used for auditability and learning analysis—e.g., to differentiate autonomous from scaffolded decisions.

---

### Notes

- The entire `memory` object is optional and only included when explicitly queried or available.
- Memory-derived fields are **advisory**, not deterministic. They should never override caregiver corrections or clarified decisions.
- Systems must clearly separate memory-boosted outcomes from independently inferred ones during training and evaluation.


recommendation
Do not treat memory fields as ground truth. They are advisory hints and should always be logged separately from direct classifier outputs.

## 8. Vector & Feature Metadata

This section defines how input features are represented numerically for inference, training, and reproducibility. To ensure auditability and compact logging, feature vectors should be stored externally and referenced via hash-validatable metadata.

---

### 8.1 External Feature Reference

| Field Name         | Type   | Req | Example                        | Description                                                                |
|--------------------|--------|-----|--------------------------------|----------------------------------------------------------------------------|
| `raw_features_ref` | object | ❌  | See schema below               | Structured reference to an external feature file (e.g., `.parquet`, `.npy`) |

This object must contain the following subfields:

{
"uri": "/data/u01/gesture_000023.parquet",
"hash": "sha256:abcdef1234567890...",
"encoding": "landmark_v2.1",
"dims": 128,
"format": "parquet"
}


| Subfield     | Type     | Req | Description                                                                  |
|--------------|----------|-----|------------------------------------------------------------------------------|
| `uri`        | string   | ✅  | Path or URI to the external feature file.                                    |
| `hash`       | string   | ✅  | Content hash (e.g., SHA-256) used to verify file integrity.                  |
| `encoding`   | string   | ✅  | Name and version of the encoder used (e.g., `"landmark_v2.1"`).             |
| `dims`       | integer  | ✅  | Number of dimensions in the encoded feature vector.                          |
| `format`     | string   | ✅  | File format (e.g., `"parquet"`, `"npy"`, `"npz"`).                           |

---

### 8.2 Versioning

| Field Name       | Type   | Req | Example     | Description                                                                 |
|------------------|--------|-----|-------------|-----------------------------------------------------------------------------|
| `vector_version` | string | ❌  | `"v2.1"`     | Version of the encoder used, if not included in `raw_features_ref.encoding` |

- This field is optional if `raw_features_ref.encoding` already encodes version info.
- Use only if external `raw_features_ref` schema is unavailable.

---

### Deprecated / Legacy Fields

- The `vector` field (inline float list) has been **removed** from the schema as of version `1.0.0`.
- Any embedded vectors must be stored externally and referenced via `raw_features_ref`.

---

### Recommendation

- Always use `raw_features_ref` for referencing feature arrays.
- Do not embed raw vectors in production JSON logs.
- Hash and version metadata must be validated at logging and inference time to ensure reproducibility.


## 9. AAC Output Fields

These fields describe the structured output intended for delivery to the AAC (Augmentative and Alternative Communication) system. They are populated only after an intent or phrase has been finalized by the CARE Engine or related modules.

---

## 9. AAC Output Fields

These fields describe the final structured outputs intended for delivery to the AAC (Augmentative and Alternative Communication) system. They are populated **only after** an intent or phrase has been resolved and finalized by the CARE Engine or equivalent planning modules.

---

### 9.1 Rendered Output

| Field Name      | Type   | Req | Example           | Description                                                                 |
|-----------------|--------|-----|--------------------|-----------------------------------------------------------------------------|
| `output_phrase` | string | ❌  | "I want to eat"    | Phrase to be rendered, spoken, or displayed by the AAC interface.           |
| `output_mode`   | string | ❌  | "speech"           | Mode of AAC output: "speech", "text", "symbol", or other UI modality.       |

These fields reflect the **final communicative act** as perceived by the user and external partners. The output may be shaped by prior context, memory-based planning, and/or clarification sequences.

---

### Notes

- These fields are **terminal outputs** of the CARE pipeline.
- If `output_mode` is omitted, AAC renderers should apply their **fallback or default display mode**.
- Future schema versions may support:
  - Multimodal composite output (e.g., speech + icon),
  - Language customization or localization tags,
  - Output latency metrics or timing hints.

---

### Recommendation

- Keep AAC output fields **distinct from internal state (e.g., classifier, memory)** to preserve separation between decision and delivery.
- Avoid embedding delivery-specific metadata (e.g., timing, formatting) unless required by the AAC renderer.


## 10. Schema Versioning & Field History

A3CP schemas are versioned to ensure forward compatibility, clear migration paths, and traceability of field semantics. Every record must include a `schema_version` field. New fields are added non-destructively and must be documented with introduction version and rationale.

---
## 10. Schema Versioning & Field History

A3CP schemas are versioned to ensure forward compatibility, clear migration paths, and traceability of field semantics. Every record must include a `schema_version` field. New fields are added non-destructively and must be documented with introduction version and rationale.

---

### 10.1 Required Version Field

| Field Name       | Type   | Req | Example    | Description                                                  |
|------------------|--------|-----|------------|--------------------------------------------------------------|
| `schema_version` | string | ✅  | `"1.0.0"`  | Semantic version of the schema used to validate this record. |

Use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR**: Breaking changes (e.g., field removal, renamed types)
- **MINOR**: Backward-compatible additions (e.g., new optional fields)
- **PATCH**: Fixes or clarifications (no structural impact)

---

### 10.2 Pre-Stable Versioning (until v1.0.0)

During pre-stable development, `schema_version` must still be present (e.g., `"0.9.2-dev"` or `"0.10.0-beta"`), but formal semantic versioning begins at `v1.0.0`, after which compatibility rules are strictly enforced.

A full version history will be published at or before the first stable release.

---

### 10.3 Deprecation Policy

- Fields may be marked as deprecated but should not be immediately removed.
- Deprecated fields must remain parsable in at least the next minor version.
- Field removal requires a **MAJOR** version increment and a documented migration strategy.

---

### Recommendation

Consumers must validate the `schema_version` before processing a record. A mismatch should raise a structured log warning or validation error.

---

### Notes

- Field group `context.*` refers to all subfields in the prompt and environment context group.
- Classifier output may include per-model metadata beyond simple `intent`/`confidence` keys.
- Modules handling `output_phrase` and `memory.*` fields should tolerate unknown subfields for forward compatibility.

---

### Recommendation

Update this matrix whenever a module’s responsibilities change, to prevent silent schema drift or interface mismatches.
