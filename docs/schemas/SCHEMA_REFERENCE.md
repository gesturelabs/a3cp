# SCHEMA_REFERENCE.md
v 1.1

This document defines the canonical runtime data schema used across all A3CP modules for internal communication and logging. The schema is represented as a `pydantic` model (`A3CPMessage`) under `schemas/a3cp_message/a3cp_message.py` and is exported as JSON Schema from the same directory.
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

All internal communication in A3CP uses a canonical structure: `A3CPMessage`.

Each message is:
- Serialized as JSON
- Validated at runtime using Pydantic
- Exported as JSON Schema from `schemas/`
- Logged as `.jsonl` under `logs/users/` and `logs/sessions/`

The schema ensures consistent interoperability across modules handling:
- Multimodal input (gesture, speech, audio, image)
- Classifier inference and confidence scoring
- Clarification, memory-based adjustment, and AAC output

Messages are:
- Versioned (`schema_version`)
- Uniquely identifiable (`record_id`)
- Grouped by interaction (`session_id`)

All modules MUST validate `schema_version` and tolerate unknown optional fields for forward compatibility.


---
## 2. Core Metadata Fields

These fields are required in every `A3CPMessage`. They provide version control,
traceability, session grouping, modality tagging, and audit timestamps.

These fields collectively constitute the Session Spine and MUST be propagated unchanged across modules unless explicitly owned and mutated by the authoritative module (e.g., `session_manager` for `session_id`).

All timestamps must use ISO 8601 format with millisecond precision and a "Z" suffix.

+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+
| Field          | Type           | Req | Example                                      | Description                                                   |
+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+
| schema_version | str            | ✅  | "1.0.0"                                      | Semantic version of the schema (MAJOR.MINOR.PATCH)            |
| record_id      | UUID           | ✅  | "07e4c9ff-9b8e-4d3e-bc7c-2b1b1731df56"         | Unique ID for this message (UUIDv4, immutable once assigned)  |
| user_id        | str            | ✅  | "elias01"                                    | Pseudonymous user identifier                                  |
| session_id     | str            | ❌  | "a3cp_sess_2025-06-15_elias01"               | Assigned by `session_manager` to group related inputs         |
| timestamp      | datetime       | ✅  | "2025-06-15T12:34:56.789Z"                   | ISO 8601 UTC timestamp with milliseconds and "Z" suffix       |
| modality       | str            | ❌  | "gesture"                                    | Input type; must use controlled vocabulary                    |
| source         | str            | ✅  | "gesture_classifier"                         | Name of the module emitting this message                      |
| performer_id   | str            | ❌* | "carer01"                                    | Actor performing input; required for human-originated inputs  |
+----------------+----------------+-----+----------------------------------------------+---------------------------------------------------------------+

(*) `performer_id` is required for all human-originated inputs. For system-generated messages, it must be set to `"system"` or may be omitted if explicitly validated as system-originated.

Notes:
- `record_id` must be UUIDv4 and immutable.
- `schema_version` must follow Semantic Versioning (MAJOR.MINOR.PATCH).
- `modality` must be one of: `"gesture"`, `"audio"`, `"speech"`, `"image"`, `"multimodal"`.
- `source` is a free-form string identifying the emitting module (no fixed enumeration).
- All timestamps must be UTC with millisecond precision and include the `"Z"` suffix.
- Consumers must treat `modality` as an enum and reject invalid values.

Allowed Values:
- `modality`: `"gesture"`, `"audio"`, `"speech"`, `"image"`, `"multimodal"`
- `performer_id`: pseudonymous identifier (e.g., `"user123"`, `"carer01"`) or `"system"`
-----------------------------


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
| sequence_id         | str      | ❌  | "elias01_000023"                           | Optional identifier for this input frame or utterance       |
| frame_index         | int      | ❌  | 23                                         | Index of this frame within the segment or sequence          |
+---------------------+----------+-----+--------------------------------------------+-------------------------------------------------------------+

Notes:
- `timestamp` must follow the formatting constraints defined in Section 2.
- If `sequence_id` is present, it must be unique within the session.
- `frame_index` is used for aligning dense input streams (e.g., video frames, audio windows, skeletal keypoints).
- `sequence_id` and `stream_segment_id` are independent; either may be used depending on stream architecture.

---

### 3.2 Input Signal Metadata

+---------------+----------+-----+------------------------+--------------------------------------------------------------+
| Field Name    | Type     | Req | Example                | Description                                                  |
+---------------+----------+-----+------------------------+--------------------------------------------------------------+
| modality      | str      | ❌  | "gesture"              | See Section 2 (Core Metadata Fields).                       |
| source        | str      | ❌  | "gesture_classifier"   | See Section 2 (Core Metadata Fields).                       |
| device_id     | str      | ❌  | "jetson_nano_01"       | Hardware identifier of the capture device.                  |
| is_demo       | bool     | ❌  | false                  | Whether this is a synthetic/test/demo sample.               |
| consent_given | bool     | ❌  | true                   | Indicates whether informed consent was captured.            |
+---------------+----------+-----+------------------------+--------------------------------------------------------------+

Notes:
- `modality` and `source` are defined canonically in Section 2 and must follow those constraints.
- `modality` may be omitted in initial raw inputs but must be populated by classifier modules.
- `device_id`, `is_demo`, and `consent_given` are optional metadata fields for traceability and ethics compliance.



## 4. Contextual Tags

This section defines optional fields that situate the input within its surrounding physical, social, or interactional environment. These fields are particularly important for disambiguating intent, modeling behavioral patterns, and providing priors to downstream modules such as the CARE Engine or Clarification Planner.

All fields in this section are optional but strongly encouraged when available.

---

### 4.1 Prompt & Environment Context

These fields are grouped under the nested `context` object.

| Field Path                   | Type   | Req | Description |
|------------------------------|--------|-----|-------------|
| `context.location`           | string | ❌  | Coarse location or room tag (e.g., "kitchen"). |
| `context.prompt_type`        | string | ❌  | Interaction type (e.g., "prompted", "natural_use", "other"). |
| `context.partner_speech`     | string | ❌  | Verbatim or paraphrased partner utterance preceding the action. |
| `context.session_notes`      | string | ❌  | Freeform caregiver notes or environment annotations. |

Notes:
- All `context.*` fields MUST be implemented as a nested object under `"context"`.
- Flat key notation (e.g., `"context_location"`) is prohibited.
- The entire `context` object is optional and may be omitted if no contextual data is available.


---

### 4.2 Derived Context Tags _(planned for future versions)_

These fields are computed post-recording by NLP or memory subsystems. They are optional and **not active in schema version 1.0.0**.

| Field Path                   | Type   | Req | Example                         | Description                                                   |
|------------------------------|--------|-----|----------------------------------|---------------------------------------------------------------|
| `context.topic_tag`          | string | ❌  | "food"                           | Inferred topic derived from partner speech or other cues.     |
| `context.relevance_score`    | float  | ❌  | 0.87                             | Confidence score for contextual relevance.                    |
| `context.flags`              | object | ❌  | { "question_detected": true }    | Map of boolean context flags.                                 |

`context.flags` may include:

- `"question_detected"` — Whether the partner speech was a question.
- `"ambiguous_intent"` — Whether the user action appeared ambiguous.
- `"requires_attention"` — Whether a caregiver manually flagged the situation.

Notes:
- These fields extend the nested `context` object defined in Section 4.1.
- Flat key notation is prohibited.
- Derived context tags are advisory metadata and must not override classifier or caregiver decisions.


## 5. Classifier Output & Label Fields

This section captures intent predictions and label provenance across modalities,
including AI inference, human annotation, correction, and final resolution.

It documents the progression from:
- Initial classifier output
- Per-modality contributions
- Human or caregiver correction
- Final resolved decision

Used by: classifier modules, input broker, clarification planner, feedback logger, CARE engine.

---

### 5.1 classifier_output_components

Per-modality AI predictions contributing to the final decision.

+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+
| Field Name                   | Type   | Req | Example                    | Description                                                  |
+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+
| classifier_output_components | object | ❌  | See subfields              | Per-modality predictions keyed by modality (e.g., "gesture") |
+------------------------------+--------+-----+----------------------------+--------------------------------------------------------------+

Each modality entry contains:

+------------+-----------+-----+----------------------------+-------------------------------------------------------------+
| Subfield   | Type      | Req | Example                    | Description                                                 |
+------------+-----------+-----+----------------------------+-------------------------------------------------------------+
| intent     | string    | ✅  | "I love you"               | Predicted intent label from this modality                   |
| confidence | float     | ✅  | 0.82                       | Confidence score between 0.0 and 1.0                        |
| timestamp  | datetime  | ✅  | "2025-07-31T10:15:01.123Z" | ISO 8601 UTC time the prediction was generated              |
+------------+-----------+-----+----------------------------+-------------------------------------------------------------+

Notes:
- Keys must correspond to valid `modality` values defined in Section 2.
- Each modality entry MUST include its own `timestamp`, representing prediction generation time.
- This timestamp is distinct from the message-level `timestamp`, which represents message emission time.
- This structure supplements but does not replace the final resolved decision fields.


---

### 5.2 classifier_output

`classifier_output` represents a per-modality confidence distribution over intent labels.

It MUST contain the raw distribution produced by a classifier module (e.g., `gesture_classifier`, `sound_classifier`, etc.). It MUST NOT represent only a fused top-1 decision.

| Field Name        | Type                  | Req | Example                                                  | Description                                                  |
|-------------------|-----------------------|-----|----------------------------------------------------------|--------------------------------------------------------------|
| classifier_output | dict[string, float]   | ❌  | { "eat": 0.62, "drink": 0.21, "unknown": 0.17 }         | Per-modality confidence distribution over intent labels.    |

#### Constraints

- Each value MUST be between `0.0` and `1.0`.
- The key `"unknown"` MUST always be present.
- For reject cases:
  - `"unknown": 1.0`
  - All other intents MUST be `0.0`.
- For accepted predictions:
  - `"unknown": 0.0`
  - Remaining values SHOULD sum to `1.0`.
- Ranking MUST be derived by sorting confidence values in descending order.
- Distribution normalization is enforced at module logic level, not JSON Schema.

#### Notes

- `classifier_output` represents the output of a single modality classifier.
- Multimodal fusion occurs downstream (e.g., in `input_broker` and `confidence_evaluator`) and MUST NOT overwrite per-modality distributions.
- A resolved top-1 decision, if required, is derived downstream and may populate `final_decision`, not `classifier_output`.
- `classifier_output` MUST remain distinct from `classifier_output_components` (if used for multi-stage aggregation).



## 6. Clarification & Feedback

This section captures the system’s capacity to detect ambiguity (clarification), refine or override intent classification (label_correction), and finalize communicative output (final_decision). It includes structured metadata for triggering clarification, human intervention, and outcome tracking.

All fields are optional unless required by a specific module (e.g., feedback logger or session manager).

---

### 6.1 Label Status & Corrections

+--------------------+---------+-----+------------------+-------------------------------------------------------------+
| Field Name         | Type    | Req | Example          | Description                                                 |
+--------------------+---------+-----+------------------+-------------------------------------------------------------+
| label_status       | string  | ❌  | "confirmed"      | Trust status of the current label.                          |
| label_correction   | string  | ❌  | "drink"          | Human override of the model or user label, applied post-inference. |
+--------------------+---------+-----+------------------+-------------------------------------------------------------+

Allowed values for `label_status`:
- `"unconfirmed"` — Initial annotation without verification.
- `"confirmed"` — Human-reviewed or validated.
- `"corrected"` — Model label has been overridden.

Notes:
- `label_correction` MUST only be populated by trusted human actors (e.g., caregivers, expert annotators).
- If `label_correction` is present, `label_status` SHOULD be set to `"corrected"`.
- `label_correction` does not replace audit fields in `classifier_output_components`; it represents post-inference intervention.

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
| final_decision   | string  | ❌  | "eat"     | Final resolved intent after clarification or correction.    |
| output_type      | string  | ❌  | "intent"  | Output category. One of: "intent", "clarification", "none". |
+------------------+---------+-----+-----------+-------------------------------------------------------------+

Allowed values for `output_type`:
- `"intent"` — Final user intent has been resolved.
- `"clarification"` — Follow-up required to disambiguate.
- `"none"` — No output generated (e.g., inconclusive input).

Rules:
- `final_decision` MUST only be set after resolution is complete.
- If `final_decision` is set, `output_type` SHOULD be `"intent"`.
- These fields MUST remain distinct from `classifier_output` and represent post-clarification outcomes only.

---

### 6.4 Clarification Metadata

All clarification planning metadata is grouped under the optional `clarification` object. This object is written by the clarification planner and consumed by downstream modules (e.g., llm_clarifier, feedback_log, memory_interface).

+------------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+
| Field Path                         | Type             | Req | Example                          | Description                                                  |
+------------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+
| clarification.needed               | boolean          | ✅  | true                             | Whether clarification should be initiated.                   |
| clarification.reason               | string           | ❌  | "low_confidence"                 | Explanation for triggering clarification.                    |
| clarification.candidates           | list[string]     | ❌  | ["eat", "drink"]                 | Ambiguous or top competing intent predictions.               |
| clarification.confidence_scores    | list[float]      | ❌  | [0.38, 0.36]                     | Confidence values aligned with `candidates`.                 |
| clarification.threshold_used       | float            | ❌  | 0.40                             | Decision threshold that triggered clarification logic.       |
+------------------------------------+------------------+-----+----------------------------------+--------------------------------------------------------------+

Notes:
- If the `clarification` object is present, `clarification.needed` MUST be included.
- If `clarification.needed` is `false`, the entire `clarification` object SHOULD be omitted.
- `clarification.*` fields are advisory metadata for interaction planning and MUST NOT resolve or override `final_decision`.



## 7. Memory-Based Output

This section contains optional fields populated by the CARE Engine’s memory modules. These fields trace whether past interactions, frequency counts, or adaptive user weights influenced the decision pipeline.

All fields below are part of the optional `memory` object and only appear when memory was queried.

---

### 7.1 User-Specific Boosts

| Field Path             | Type                | Req | Example                          | Description                                                                 |
|------------------------|---------------------|-----|----------------------------------|-----------------------------------------------------------------------------|
| `memory.intent_boosts` | dict[string, float] | ❌  | { "eat": 0.15, "play": 0.05 }    | Per-user intent likelihood boosts derived from prior interaction history.  |

Notes:
- This field is part of the nested `memory` object.
- Values represent additive or weighting adjustments applied during fusion.
- These boosts are advisory and MUST NOT be treated as ground truth or override caregiver corrections.
---

### 7.2 Fallback Suggestions

| Field Path                    | Type          | Req | Example                     | Description                                                                 |
|-------------------------------|---------------|-----|-----------------------------|-----------------------------------------------------------------------------|
| `memory.fallback_suggestions`| list[string]  | ❌  | ["rest", "drink", "eat"]    | Ranked list of intents from memory used when classifier confidence is low. |

Notes:
- This field is part of the nested `memory` object.
- Suggestions MUST be ordered by descending estimated relevance.
- These suggestions are advisory and may be presented for caregiver selection.
- They MUST NOT override `final_decision` or human corrections automatically.

---

### 7.3 Hint Usage Flag

| Field Path            | Type    | Req | Example | Description                                                                 |
|-----------------------|---------|-----|---------|-----------------------------------------------------------------------------|
| `memory.hint_used`    | boolean | ❌  | true    | Indicates whether memory-based hints contributed to the final decision.     |

Notes:
- This field is part of the nested `memory` object.
- It supports auditability and learning analysis (e.g., differentiating autonomous from scaffolded decisions).
- It must reflect whether memory influenced the fusion or final decision stage.

---

### Notes

- The entire `memory` object is optional and MUST only be included when explicitly queried or applied.
- Memory-derived fields are advisory and MUST NOT override caregiver corrections, clarified decisions, or `final_decision`.
- Systems must clearly separate memory-influenced outcomes from independently inferred classifier outputs during training, evaluation, and audit.
- Memory fields must never be treated as ground truth and must remain distinct from raw classifier predictions in logs.


## 8. Vector & Feature Metadata

This section defines how input features are represented numerically for inference, training, and reproducibility. To ensure auditability and compact logging, feature vectors should be stored externally and referenced via hash-validatable metadata.

---

### 8.1 External Feature Reference

| Field Path               | Type   | Req | Example              | Description                                                      |
|--------------------------|--------|-----|----------------------|------------------------------------------------------------------|
| `raw_features_ref`       | object | ❌  | See schema below     | Structured reference to an external feature file.               |

Notes:
- `raw_features_ref` is used to reference externally stored feature vectors.
- Inline embedding of full feature arrays in production logs is prohibited.


Example `raw_features_ref` structure (using `.npz`):

{
  "uri": "/data/u01/gesture_000023.npz",
  "hash": "sha256:abcdef1234567890...",
  "encoding": "landmark_v2.1",
  "dims": 128,
  "format": "npz"
}

Constraints:
- `uri` MUST reference a valid `.npz` file.
- `hash` MUST be a SHA-256 content hash of the `.npz` file.
- `encoding` MUST specify encoder name and version.
- `dims` MUST match the dimensionality of the stored vector.
- `format` MUST be `"npz"` for this configuration.



| Subfield   | Type    | Req | Description                                                                 |
|------------|---------|-----|-----------------------------------------------------------------------------|
| `uri`      | string  | ✅  | Path or URI to the external `.npz` feature file.                          |
| `hash`     | string  | ✅  | SHA-256 content hash of the referenced file for integrity verification.   |
| `encoding` | string  | ✅  | Encoder name and version (e.g., `"landmark_v2.1"`).                        |
| `dims`     | integer | ✅  | Dimensionality of the encoded feature vector.                               |
| `format`   | string  | ✅  | File format; MUST be `"npz"` for this configuration.                       |


---

### 8.2 Versioning

| Field Name       | Type   | Req | Example  | Description                                                              |
|------------------|--------|-----|----------|--------------------------------------------------------------------------|
| `vector_version` | string | ❌  | "v2.1"   | Encoder version, used only when `raw_features_ref` is absent.           |

Notes:
- If `raw_features_ref` is present, `vector_version` SHOULD NOT be set.
- `raw_features_ref.encoding` is the authoritative source of encoder version.
- This field exists for backward compatibility or minimal-record scenarios only.




### Recommendation

- Always use `raw_features_ref` for referencing feature arrays.
- Do not embed raw vectors in production JSON logs.
- Hash and version metadata must be validated at logging and inference time to ensure reproducibility.




## 9. AAC Output Fields

These fields describe the final structured outputs intended for delivery to the AAC (Augmentative and Alternative Communication) system. They are populated **only after** an intent or phrase has been resolved and finalized by the CARE Engine or equivalent planning modules.

---

### 9.1 Rendered Output

### 9.1 Rendered Output

| Field Name      | Type   | Req | Example           | Description                                                                 |
|-----------------|--------|-----|--------------------|-----------------------------------------------------------------------------|
| `output_phrase` | string | ❌  | "I want to eat"    | Final phrase to be rendered, spoken, or displayed by the AAC interface.    |
| `output_mode`   | string | ❌  | "speech"           | Output modality (e.g., "speech", "text", "symbol").                        |

Notes:
- These fields represent the final communicative act after resolution.
- If `output_phrase` is set, `final_decision` SHOULD also be set.
- `output_mode` controls delivery modality only and MUST NOT affect intent resolution.

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

During pre-stable development, `schema_version` MUST still be present (e.g., `"0.9.2-dev"` or `"0.10.0-beta"`).

Formal semantic versioning rules (strict compatibility guarantees) apply starting at `v1.0.0`.

Before `v1.0.0`:
- Backward compatibility is not guaranteed.
- Field additions, renames, or structural changes may occur.
- Consumers SHOULD validate exact version matches.

A complete version history MUST be published at or before the first stable release.

---

### 10.3 Deprecation Policy

- Fields may be marked as deprecated but MUST NOT be immediately removed.
- Deprecated fields MUST remain parsable for at least one subsequent MINOR version.
- Field removal requires a MAJOR version increment and a documented migration strategy.
- Deprecation status SHOULD be explicitly documented in this file with version and rationale.


---

### Recommendation

Consumers MUST validate `schema_version` before processing a record.
- A MAJOR version mismatch MUST raise a validation error.
- A MINOR or PATCH mismatch SHOULD raise a structured log warning.

---

### Notes

- `context.*` refers to all subfields within the nested `context` object.
- `classifier_output` may include additional per-model metadata beyond `intent` and `confidence`.
- Modules handling `output_phrase` and `memory.*` fields MUST tolerate unknown subfields for forward compatibility.

---

### Recommendation

This document MUST be updated whenever a module’s responsibilities or field semantics change, to prevent silent schema drift or interface mismatches.
