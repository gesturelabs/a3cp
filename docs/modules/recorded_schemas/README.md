# Module: recorded_schemas

## Purpose
The `recorded_schemas` module serves as the persistent, structured memory of the A3CP runtime. It receives validated `A3CPMessage` records from the `schema_recorder` and stores them in an immutable, queryable archive. These records form the foundation for model retraining, audit logging, playback, and visualization workflows.

## Why It Matters
A3CP depends on a verifiable, reproducible record of all interactions to support transparency, learning, and feedback integration. This module enables consistent training, review, and visualization by ensuring that all multimodal interaction records are safely stored, integrity-checked, and accessible by downstream modules.

## Responsibilities
- Receive fully validated `A3CPMessage` records from the `schema_recorder`
- Store records in an append-only format (e.g., `.jsonl`, database row, object store)
- Ensure referential integrity for any externally stored features (e.g., `raw_features_ref`)
- Index messages by `record_id`, `session_id`, `user_id`, and `modality`
- Support fast lookup and batch export for:
  - Model retraining (`model_trainer`)
  - Landmark and sound visualization (`landmark_visualizer`, `sound_playback`)
  - Feedback-driven adaptation (`retraining_scheduler`)

## Not Responsible For
- Validating or modifying `A3CPMessage` contents (handled upstream)
- Performing inference or classification
- Creating derived features or training splits (handled by `model_trainer`)
- Rendering UI or partner-facing outputs

## Inputs
- `A3CPMessage` objects from `schema_recorder`, including:
  - Full structured schema (timestamp, user_id, session_id, modality, etc.)
  - Optional `raw_features_ref` with URI and hash
  - Optional clarification, feedback, and memory fields

## Outputs
- Persistent, queryable archive of `A3CPMessage` records
- Batch exports to:
  - `model_trainer` (training datasets)
  - `sound_playback` (gesture/audio replay)
  - `landmark_visualizer` (skeletal and visual feedback)
  - `retraining_scheduler` (label correction triggers, annotation tools)

## CARE Integration
`recorded_schemas` is the central memory store for the entire A3CP runtime. It acts as the source of truth for what was observed, inferred, and corrected during a session. All downstream retraining, memory updates, and partner feedback resolution rely on its accuracy and completeness.

## Functional Requirements
- F1. Store every incoming `A3CPMessage` as-is with no mutation
- F2. Guarantee message order (append-only)
- F3. Support filtering by session, modality, user, or timestamp
- F4. Ensure feature integrity using file hash (`sha256`) in `raw_features_ref`
- F5. Enable efficient batch export of data slices for training and review

## Non-Functional Requirements
- NF1. Must support high-throughput message ingestion (≥100 msg/sec)
- NF2. Storage must be durable and fault-tolerant
- NF3. Must reject duplicate `record_id` values if integrity is violated
- NF4. Export latency for retraining workflows must be <2s for 1k records
- NF5. Query interface must support reproducible retrieval (e.g., sorted `.jsonl` or indexed DB)

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [a3cp_message_record.json](./a3cp_message_record.json)
- [export_training_slice.json](./export_training_slice.json)
- [record_index_query.json](./record_index_query.json)
- [schema.json](./schema.json)
