# Submodule: RecordingPipeline

## Purpose
Serializes and saves landmark sequences with intent labels and contextual metadata for use in training, audit, and reproducibility.

## Responsibilities
- Accumulate timestamped landmark vectors into sequences
- Attach metadata such as:
  - `session_id`, `user_id` or `pseudonym`, `intent_label`, `timestamp`
- Validate sequences against schema v1.0 (`RawActionRecord`)
- Serialize validated records to durable format (e.g., `.parquet`, `.jsonl`)
- Log provenance metadata (e.g., time of write, source module)

## Not Responsible For
- Capturing video frames
- Extracting landmarks (handled by `LandmarkExtractor`)
- Running inference/classification
- Initiating or managing training workflows

## Inputs
- Landmark vectors (with frame-level timestamps) from `LandmarkExtractor`
- Session and user metadata from upstream controller
- Intent label (entered by user or caregiver)

## Outputs
- Schema-compliant training records (`RawActionRecord`)
- Serialized files written to disk (e.g., `data/session_<ID>/record_<UUID>.parquet`)
- Append-only provenance logs (e.g., `provenance.jsonl`)

## Runtime Considerations
- Landmark buffers must be stored safely in memory until intent label is confirmed
- Disk write operations must be atomic (avoid partial/corrupt files)
- All output must be schema-validated (v1.0) before write
- Each saved record must include all required audit fields

## Open Questions
- Should we support:
  - Appending to session-level files?
  - One-record-per-file serialization?
- How do we handle re-labeling or correction of labels post-write?
- If schema validation fails, should data be cached or discarded?
- What is the fallback procedure for disk I/O failure?

## Notes
- This module is central to the system’s auditability and training traceability
- It does **not** control the labeling UI — intent labels are passed to it externally
- All writes should be accompanied by entry in the provenance log, linked by a unique `record_id` or `action_id`
