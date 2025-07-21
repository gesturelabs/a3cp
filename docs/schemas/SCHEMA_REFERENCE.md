# SCHEMA_REFERENCE.md

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

All inter-module messages in A3CP are wrapped in a versioned, validated `A3CPMessage` structure. These messages are:

- Serialized as JSON
- Validated at runtime using `pydantic`
- Mirrored by a public-facing JSON Schema in `interfaces/`
- Logged in `.jsonl` format under `logs/users/` and `logs/sessions/`

The message format supports multimodal input (gesture, sound), contextual profiling, classifier decisions, clarification tracking, and memory-informed suggestions.

---
## 2. Core Metadata Fields

These fields form the foundation of every `A3CPMessage`. They are mandatory for all records and ensure global traceability, auditability, and runtime validation. All timestamps must be in UTC ISO 8601 format with milliseconds.

| Field             | Type     | Req | Example                                  | Description                                                                 | Version |
|------------------|----------|-----|------------------------------------------|-----------------------------------------------------------------------------|---------|
| `schema_version` | string   | ✅  | `"1.0.0"`                                | Semantic version (`MAJOR.MINOR.PATCH`) of the schema used for validation.  | 1.0     |
| `record_id`      | UUID     | ✅  | `"07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56"` | Globally unique identifier for this message (UUIDv4 recommended).          | 1.0     |
| `user_id`        | string   | ✅  | `"elias01"`                              | Pseudonymous user identifier.                                               | 1.0     |
| `session_id`     | string   | ✅  | `"a3cp_sess_2025-06-15_elias01"`         | Unique ID for a logically grouped interaction session.                     | 1.0     |
| `timestamp`      | datetime | ✅  | `"2025-06-15T12:34:56.789Z"`             | UTC timestamp in ISO 8601 format with millisecond precision.               | 1.0     |
| `modality`       | string   | ✅  | `"gesture"`                              | Input type: one of `"gesture"`, `"audio"`, `"speech"`, `"image"`, etc.     | 1.0     |
| `source`         | string   | ✅  | `"communicator"`                         | Origin of input: `"communicator"`, `"caregiver"`, or `"system"`.           | 1.0     |

### Allowed Values

- `modality`: `"gesture"`, `"audio"`, `"speech"`, `"image"`, `"multimodal"`
- `source`: `"communicator"`, `"caregiver"`, `"system"`

### Notes

- `schema_version` must be present in all records and follow strict semantic versioning.
- `record_id` must be globally unique (UUIDv4 preferred) and immutable across logs.
- `modality` and `source` should be treated as enums to prevent invalid values.
- All timestamps must be in UTC with millisecond precision (e.g., `"Z"` suffix required).

## Section 3: Input & Stream Fields

This section defines all fields related to raw input collection, temporal sequencing, stream segmentation, and modality-specific metadata. These fields are primarily used by the Streamer, Sensor Capture Interfaces, and Logger modules.

### 3.1 Temporal Structure & Stream Windowing

| Field Name          | Type     | Req | Example                                  | Description                                                                |
|---------------------|----------|-----|------------------------------------------|----------------------------------------------------------------------------|
| `timestamp`         | datetime | ✅  | "2025-05-05T12:31:46.123Z"               | ISO 8601 UTC timestamp of when the input was captured.                     |
| `stream_segment_id` | string   | ❌  | "elias01_2025-05-05T12:31:45Z"           | Optional window or chunk ID for stream segmentation.                       |
| `sequence_id`       | string   | ❌  | "elias01_000023"                         | Optional global sequence identifier for this input frame or utterance.    |
| `frame_index`       | integer  | ❌  | 23                                       | Index of this frame in the current sequence or stream segment.            |

- If `sequence_id` is present, it should be unique within the session.
- `frame_index` is used for alignment of dense sensor streams (e.g., skeletal frames).

---

### 3.2 Input Signal Metadata

| Field Name      | Type     | Req | Example               | Description                                                                  |
|-----------------|----------|-----|------------------------|------------------------------------------------------------------------------|
| `modality`      | string   | ✅  | "gesture"             | Type of input, e.g., "gesture", "audio", "image", "multimodal".              |
| `source`        | string   | ✅  | "communicator"        | Who generated the input: "communicator", "caregiver", "system".              |
| `device_id`     | string   | ❌  | "jetson_nano_01"      | Hardware identifier of the capture device.                                   |
| `is_demo`       | boolean  | ❌  | false                 | Whether this is a synthetic/test/demo sample.                                |
| `consent_given` | boolean  | ❌  | true                  | Indicates whether informed consent was captured for this input.              |

**Notes:**
- `modality` and `source` must use controlled vocabularies (see Section 2).
- `is_demo` and `consent_given` are used for ethics filtering and training logic.
---

### 3.3 Vector Encoding & Feature Extraction


| Field Name         | Type     | Req | Example                        | Description                                                               | Version   |
|--------------------|----------|-----|--------------------------------|---------------------------------------------------------------------------|-----------|
| `vector_version`   | string   | ❌  | "v2.1"                         | Version of the vector encoder used to produce features.                   | v1.0      |
| `raw_features_ref` | object   | ❌  | see schema below               | Reference to external vector file or array.                               | v1.0      |

#### `raw_features_ref` schema

```json
{
  "uri": "/data/elias01/gesture_000023.parquet",
  "hash": "sha256:abcdef1234567890...",
  "encoding": "landmark_v2.1",
  "dims": 128,
  "format": "parquet"
}
```

| Subfield     | Type     | Req | Description                                                           |
|--------------|----------|-----|-----------------------------------------------------------------------|
| `uri`        | string   | ✅  | Path or URI to vector file (e.g., `.parquet`, `.npz`, or `.npy`).     |
| `hash`       | string   | ✅  | Content hash (e.g., SHA-256) of the vector file.                      |
| `encoding`   | string   | ✅  | Name and version of the encoder used (e.g., "landmark_v2.1").         |
| `dims`       | integer  | ✅  | Dimensionality of the vector.                                         |
| `format`     | string   | ✅  | File format of the stored vector (e.g., "parquet", "npy", "npz").     |

-vector is deprecated and should be used only for unit tests with vectors < 5 elements.
-All production logs must use raw_features_ref with integrity hash.
-Future schema versions may require vector_version to match encoding.

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

## 5. Classifier Output & Label Fields

This section captures the evolving interpretation of an input—from initial AI classification to human annotation and clarification. These fields may be populated at different stages of the CARE loop, and should be treated as distinct sources of label provenance.

---

### 5.1 User Labeling

| Field Name       | Type     | Req | Example         | Description                                                                 |
|------------------|----------|-----|------------------|-----------------------------------------------------------------------------|
| `intent_label`   | string   | ❌  | `"help"`         | Initial human-annotated or user-assigned intent label.                      |
| `label_status`   | string   | ❌  | `"unconfirmed"`  | Status of the label. One of: `"unconfirmed"`, `"confirmed"`, `"corrected"`. |

- `intent_label` may come from early annotation or user reporting.
- `label_status` tracks the trust level of `intent_label`, especially for training splits.

---

### 5.2 Classifier Output

| Field Name          | Type   | Req | Example                                   | Description                                                                 |
|---------------------|--------|-----|-------------------------------------------|-----------------------------------------------------------------------------|
| `classifier_output` | object | ❌  | `{ "intent": "eat", "confidence": 0.91 }` | Output of AI model inference. Expected keys: `intent` (string), `confidence` (float). |

- This field is typically generated by modules like `gesture_classifier`, `sound_classifier`, etc.
- Additional keys (e.g. `model_version`, `ranking`, `timestamp`) may be added per implementation.

---

### 5.3 Caregiver Overrides and Final Clarification

| Field Name         | Type     | Req | Example     | Description                                                                     |
|--------------------|----------|-----|-------------|---------------------------------------------------------------------------------|
| `label_correction` | string   | ❌  | `"drink"`   | Caregiver-assigned corrected label, replacing `intent_label`.                  |
| `final_decision`   | string   | ❌  | `"drink"`   | Final decision after all clarification steps, used for output and training.    |
| `output_type`      | string   | ❌  | `"intent"`  | One of: `"intent"`, `"clarification"`, `"none"`. Indicates type of final output. |

- `final_decision` should only be populated after clarification, override, or planning is complete.
- `output_type` supports downstream renderers and UI filters.

---

### Label Source Comparison

| Field             | Origin         | Overwrites | Trust Level | Purpose                          |
|------------------|----------------|------------|-------------|----------------------------------|
| `intent_label`   | Human/User     | No         | Low-Med     | Initial input from user/human    |
| `classifier_output_intent` | AI/Model | No     | Medium      | Initial system prediction        |
| `label_correction` | Caregiver    | Yes        | High        | Corrected label from caregiver   |
| `final_decision` | CARE Engine    | Yes        | Final       | Outcome for audit/training/logs  |

---

### Warning

Do **not** pre-fill `final_decision` or `output_type` before clarification is complete.
These fields should reflect **post-resolution** logic only. Pre-filling them may contaminate training labels or misrepresent system performance.

## 6. Clarification & Feedback

This section captures the system’s capacity to detect ambiguity (clarification), refine or override intent classification (label_correction), and finalize communicative output (final_decision). It includes structured metadata for triggering clarification, human intervention, and outcome tracking..

All fields are optional unless required by a specific module (e.g., feedback logger or session manager).

---

### 6.1 Label Status & Corrections

| Field Name         | Type    | Req | Example         | Description                                                                 |
|--------------------|---------|-----|------------------|-----------------------------------------------------------------------------|
| `label_status`     | string  | ❌  | `"confirmed"`    | Label trust status. One of: `"unconfirmed"`, `"confirmed"`, `"corrected"`.  |
| `label_correction` | string  | ❌  | `"drink"`        | Human override of the model or user label, applied post-inference.         |

**Allowed values for `label_status`:**
- `"unconfirmed"`: Initial annotation without verification
- `"confirmed"`: Human-reviewed or validated
- `"corrected"`: Model label has been overridden

Only trusted sources (e.g., caregivers, expert annotators) should populate `label_correction`.

---

### 6.2 Consent and Demonstration Flags

| Field Name       | Type    | Req | Example | Description                                                                 |
|------------------|---------|-----|---------|-----------------------------------------------------------------------------|
| `consent_given`  | boolean | ❌  | `true`  | Whether explicit informed consent was obtained for this input.              |
| `is_demo`        | boolean | ❌  | `false` | Whether this record is synthetic or for demonstration purposes only.        |

These flags may be used for **ethics compliance**, audit filtering, and exclusion from training pipelines.

---

### 6.3 Final Decision & Output Mode

| Field Name        | Type    | Req | Example     | Description                                                                  |
|-------------------|---------|-----|-------------|------------------------------------------------------------------------------|
| `final_decision`  | string  | ❌  | `"eat"`     | Final resolved intent after feedback, override, or clarification.            |
| `output_type`     | string  | ❌  | `"intent"`  | Output category. One of: `"intent"`, `"clarification"`, `"none"`.            |

**Allowed values for `output_type`:**
- `"intent"`: Final user intent has been resolved
- `"clarification"`: Follow-up or request for disambiguation
- `"none"`: No output was generated (e.g., inconclusive input)

**Warning:** Do not pre-populate `final_decision` or `output_type` before resolution is complete. These fields represent **post-clarification outcomes** and must be kept distinct from initial predictions.

---

### Notes

- These fields form a bridge between automated inference, human feedback, and clarified outcomes.
- Only one final interpretation (`final_decision`) should be used for training or rendering per message.
- Feedback fields must be clearly traceable and audit-tagged to distinguish them from raw AI outputs.

**Recommendation:**
Clarification is not ground truth. These fields reflect interactive resolution steps and should be logged **separately** from original classifier predictions to preserve provenance.

### 6.4 Clarification Metadata

All clarification planning metadata is grouped under the optional `clarification` object. This object is typically written by the `clarification_planner` and read by downstream modules such as the `llm_clarifier`, `feedback_log`, or `memory_interface`.

| Field                          | Type             | Req | Example                            | Description                                                                 |
|-------------------------------|------------------|-----|------------------------------------|-----------------------------------------------------------------------------|
| `clarification.needed`        | boolean           | ✅  | `true`                             | Whether clarification should be initiated for this input.                   |
| `clarification.reason`        | string            | ❌  | `"low_confidence"`                 | Explanation for triggering clarification.                                  |
| `clarification.candidates`    | list of strings   | ❌  | `["eat", "drink"]`                 | Top ambiguous or tied intent predictions.                                  |
| `clarification.confidence_scores` | list of floats | ❌  | `[0.38, 0.36]`                      | Confidence values (aligned with `candidates`).                             |
| `clarification.threshold_used`| float             | ❌  | `0.40`                             | Threshold that triggered clarification logic.                              |

This object supports structured decision logging and LLM-based prompt construction. It should be emitted **only** when clarification is required (`clarification.needed == true`).

**Notes:**
- All fields are optional except `clarification.needed`.
- If `clarification.needed` is `false`, this object may be omitted entirely.
- `clarification.*` fields are not ground truth and must be treated as advisory metadata for interaction planning, not intent resolution.



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

## 11. Module Usage Matrix

This table summarizes which A3CP modules interact with each field group in the canonical schema. It clarifies responsibilities, ensures interface stability, and tracks the lifecycle of each field across the system.

| Field / Section                | Streamer | Inference | Trainer | CARE Engine | Feedback Logger |
|-------------------------------|----------|-----------|---------|-------------|-----------------|
| `schema_version`              | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `record_id`                   | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `user_id`                     | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `session_id`                  | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `timestamp`                   | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `modality`                    | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `source`                      | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `stream_segment_id`           | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `sequence_id`, `frame_index`  | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `vector`                      | ✅ write | ✅ read    | ✅ read  | ✅ read      | ❌               |
| `raw_features_ref`            | ✅ write | ✅ read    | ✅ read  | ✅ read      | ❌               |
| `classifier_output`           | ❌       | ✅ write   | ✅ read  | ✅ read      | ✅ read          |
| `intent_label`                | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ write         |
| `label_status`                | ✅ write | ❌        | ❌      | ✅ update    | ✅ update        |
| `label_correction`            | ❌       | ❌        | ❌      | ✅ read      | ✅ write         |
| `context_*`                   | ✅ write | ✅ read    | ✅ read  | ✅ update    | ✅ write         |
| `ASR_confidence_score`        | ✅ write | ✅ read    | ✅ read  | ✅ read      | ✅ read          |
| `final_decision`              | ❌       | ❌        | ❌      | ✅ write     | ✅ write         |
| `output_type`                 | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `memory_intent_boosts`        | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `memory_fallback_suggestions` | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `memory_hint_used`            | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `output_phrase`               | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `output_mode`                 | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |
| `clarification.*`             | ❌       | ❌        | ❌      | ✅ write     | ✅ read          |


---

### Legend

- ✅ write: Field is initially created or overwritten by the module.
- ✅ update: Field may be conditionally modified after initial write.
- ✅ read: Field is accessed but not modified.
- ❌: Field is unused by the module.

---

### Notes

- Field group `context.*` refers to all subfields in the prompt and environment context group.
- Classifier output may include per-model metadata beyond simple `intent`/`confidence` keys.
- Modules handling `output_phrase` and `memory.*` fields should tolerate unknown subfields for forward compatibility.

---

### Recommendation

Update this matrix whenever a module’s responsibilities change, to prevent silent schema drift or interface mismatches.
