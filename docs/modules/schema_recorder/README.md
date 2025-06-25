# Module: schema_recorder

## Purpose
The `schema_recorder` module is responsible for validating, serializing, and persistently storing structured runtime records that conform to a registered schema (e.g., `A3CPMessage`, `RawActionRecord`). It provides a unified interface for recording any schema-compliant object in a durable, auditable, and version-tracked manner.

## Why It Matters
This module forms the backbone of A3CP’s audit, reproducibility, and retraining infrastructure. By standardizing how structured data is validated and logged, it eliminates redundant logging logic, ensures schema compliance, and preserves system-wide traceability for all recorded events and interactions.

## Responsibilities
- Validate input records against the expected schema version
- Serialize validated records to structured append-only formats (`.jsonl`, `.parquet`, etc.)
- Preserve insertion order for audit and replayability
- Log key metadata: `record_id`, `timestamp`, `schema_type`, `user_id`, `session_id`
- Optionally log source module, `action_id`, or extended provenance tags
- Ensure atomic write behavior and hashable file integrity
- Maintain schema registry to map types to storage formats and destinations

## Not Responsible For
- Performing classification, inference, or decision-making
- Modifying or enriching schema fields beyond validation
- Rendering, displaying, or dispatching outputs
- Triggering model training or running pipeline loops

## Inputs
- Any object conforming to a registered `pydantic` schema
  - e.g., `A3CPMessage`, `RawActionRecord`, `AuditEvent`
- Required metadata (may be embedded or passed externally):
  - `record_id`, `timestamp`, `schema_version`
  - `user_id`, `session_id` (if available)
  - `schema_type` (optional override if not inferred)

## Outputs
- Serialized records stored in:
  - `.jsonl` files (e.g., `logs/users/u1234/a3cp_message.jsonl`)
  - `.parquet` files (e.g., `data/session_xyz/gesture_record_001.parquet`)
- Metadata entries in provenance or audit logs
- Optional summary/index files for efficient search

## CARE Integration
The `schema_recorder` is invoked throughout the CARE pipeline wherever structured messages are finalized for storage. It is used to record:
- Incoming classified `A3CPMessage` records
- Annotated landmark sequences (`RawActionRecord`)
- CARE events and interactions (`AuditEvent`, future extensions)

It ensures that all runtime data written to disk is schema-compliant, validated, and reproducible for audit, replay, and retraining.

## Functional Requirements
- F1. Must validate all records against declared schema version
- F2. Must write records to disk in append-only fashion
- F3. Must preserve insertion order and emit atomic writes
- F4. Must hash output (if enabled) for data integrity tracking
- F5. Must support multiple schema types via registry

## Non-Functional Requirements
- NF1. Write latency must remain <50ms under normal I/O load
- NF2. Must recover cleanly from interrupted writes or invalid input
- NF3. Must support configurable log rotation and storage limits
- NF4. Must tolerate schema evolution (versioned, non-breaking changes)
- NF5. Must tag logs with module name and runtime environment for traceability

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_a3cp_message.json](./sample_a3cp_message.json)
- [sample_raw_action_record.json](./sample_raw_action_record.json)
- [schema_registry.json](./schema_registry.json)
