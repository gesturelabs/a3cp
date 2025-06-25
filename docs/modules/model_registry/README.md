# Module: model_registry

## Purpose
The `model_registry` module records detailed metadata about every trained model in A3CP, including the user it belongs to, the modality it supports, its training configuration, and the artifact's storage location. This enables reproducibility, debugging, and version tracking across training sessions and deployments.

## Why It Matters
Without model registry traceability, it becomes impossible to audit or reproduce predictions, especially in per-user systems like A3CP. This module ensures that every training event is logged and can be queried by system components, developers, or evaluators.

## Responsibilities
- Log each model training event, including `user_id`, `modality`, training `config`, `vector_version`, `timestamp`, and `model_artifact_path`.
- Generate a unique model version ID (e.g., via hash or timestamp).
- Store entries in a persistent and queryable format (e.g., `models.jsonl` or SQLite).
- Validate schema of each record to ensure audit integrity.
- Allow lookups by `user_id`, `modality`, `version`, and training parameters.

## Not Responsible For
- Performing training itself (handled by `model_trainer`).
- Performing inference (handled by `gesture_classifier`, `sound_classifier`, etc.).
- Evaluating model quality or scoring performance.

## Inputs
- `user_id`: pseudonym of the user for whom the model was trained
- `modality`: e.g., `"gesture"`, `"sound"`, `"speech"`
- `vector_version`: feature format version (e.g., `"v1.2"`)
- `timestamp`: ISO 8601 UTC timestamp
- `config`: training configuration (e.g., model type, hyperparameters, sample count)
- `model_artifact_path`: relative or absolute path to `.h5`, `.pkl`, or other saved model format

## Outputs
- Structured log entry in registry file (`model_registry.jsonl` or SQLite row)
- Metadata returned for query-based lookup:
  - `user_id`, `modality`, `model_artifact_path`, `vector_version`, `timestamp`, `schema_version`

## CARE Integration
- Queried by: `gesture_classifier`, `sound_classifier`, retraining scheduler, model auditing tools
- Supports: Inference loading, retraining reproducibility, model comparison

## Functional Requirements
- FR1. Must log every model training event with complete metadata.
- FR2. Must support lookup queries by `user_id`, `modality`, and model version.
- FR3. Must validate all input against a defined schema before saving.

## Non-Functional Requirements
- NF1. Must support both local (JSONL) and remote (SQLite or JSON-over-API) registry backends.
- NF2. Must preserve all historical entries, including retraining or superseded models.
- NF3. Must allow optional hash-based verification of model file integrity.
- NF4. Write operations must be atomic and crash-safe.

## Developer(s)
Unassigned

## Priority
High – necessary for secure inference and auditability.

## Example Files
- `model_registry.jsonl` (local flat-file format)
- `model_registry.db` (SQLite format)
- `model_entry_example.json` (schema sample)

## Open Questions
- Should this module enforce uniqueness of (user_id, modality) or allow multiple versions?
- Will we support export to external registries (e.g., Hugging Face, ONNX Zoo)?
- Should we store additional provenance (e.g., input sample hashes or training logs)?
- Should the registry support deletion or just flagging of deprecated models?
