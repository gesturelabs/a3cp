# Module: session_manager

## Purpose
The session_manager module organizes all user interactions into discrete, timestamped sessions. It assigns and tracks session identifiers, enabling linked logs for audit, caregiver review, debugging, and the construction of training datasets over coherent interaction periods.

## Why It Matters
By grouping related input, clarification, and output events under a common session_id, this module provides temporal structure to otherwise fragmented data. Sessionization is essential for replayability, caregiver context reconstruction, and understanding behavior over time. It also supports compliance, audit, and training workflows.

## Responsibilities

- Generate globally unique `session_id` values for each new interaction window per user.
- Define and emit authoritative session lifecycle boundary events (start, end).
- Record session start and end events with associated metadata.
- Ensure all session lifecycle outputs include `session_id`, `user_id`, `timestamp`, `record_id`, and `source`.
- Persist session lifecycle events as an append-only, chronological JSONL record for audit and debugging.

Session ID Propagation Contract

There is no concept of a shared or implicit “current session”.

- `session_id` is generated only by `session_manager`.
- Callers (UI, workers) MUST store and explicitly propagate `session_id`.
- Workers MUST reject requests missing `session_id` (400) at ingress.
- `session_manager` does not expose any API to infer or query a current session.

Multi-worker note (current demo implementation)

The session manager keeps session state in process-local memory (`_sessions`) only to validate `/sessions.end`. Therefore, `/sessions.start` and `/sessions.end` must be handled by the same process for reliable operation (run `session_manager` as single-worker or use sticky routing).

This does **not** provide or imply any “current session” lookup.


## Not Responsible For
- Performing inference, classification, or clarification logic.
- Storing raw media (video, audio, images).
- Determining label correctness or intent validity.

## Public Contracts
The session_manager exposes two lifecycle actions, each defined by an input/output schema pair and exported via the `schemas` public surface.

Canonical exported names:
- SessionManagerStartInput
- SessionManagerStartOutput
- SessionManagerEndInput
- SessionManagerEndOutput

Current implementation classes:
- SessionStartInput / SessionStartOutput
  (schemas/session_manager/session_manager_start/session_manager_start.py)
- SessionEndInput / SessionEndOutput
  (schemas/session_manager_end/session_manager_end.py)

Downstream modules MUST depend only on the canonical exported names, not on internal class names or file paths.

## Inputs
- Session inputs originate from UI actions, system triggers, or caregiver-initiated workflows.
- All inputs inherit BaseSchema and MUST conform to docs/schemas/SCHEMA_REFERENCE.md (v1.1).
- Core metadata fields (schema_version, record_id, user_id, timestamp) are required.
- All timestamps MUST be UTC ISO 8601 with millisecond precision and a “Z” suffix.
- performer_id is required for human-originated inputs.
- session_id is assigned by session_manager and is REQUIRED when ending a session.

## Outputs
- All outputs inherit BaseSchema and conform to SCHEMA_REFERENCE.md (v1.1).
- session_id is REQUIRED on all session_manager outputs.
- source SHOULD be set to "session_manager".
- Outputs represent authoritative session boundary events and metadata only.

**Note:** In a multi-service deployment, downstream modules MUST NOT query
`session_manager` for a “current session”. The `session_id` emitted in these
outputs is intended to be propagated explicitly (e.g., by the UI/orchestrator)
to all downstream workers.

## CARE Integration
The session_manager provides the temporal spine for CARE Engine operation. All CARE-related inputs and outputs are grouped by session_id, enabling replay, audit, clarification analysis, and training dataset construction without altering message semantics.

## Functional Requirements
- F1. Generate unique, stable session_ids per user per session.
- F2. Detect and log session boundaries (start/end).
- F3. Tag all CARE-related messages with the active session_id.
- F4. Support chronological replay and export of session timelines.
- F5. Persist session metadata across restarts.


## Non-Functional Requirements
- NF1. Session tracking must survive temporary disconnects and restarts.
- NF2. Session tagging must remain low-latency.
- NF3. Session logs must be append-only and audit-compliant.
- NF4. Session IDs must be globally unique and stable.
- NF5. Both timeout-driven and explicit termination must be supported.

## Priority
High
