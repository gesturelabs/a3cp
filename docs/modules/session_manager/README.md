# Module: session_manager

## Purpose
The session_manager module organizes all user interactions into discrete, timestamped sessions. It assigns and tracks session identifiers, enabling linked logs for audit, caregiver review, debugging, and the construction of training datasets over coherent interaction periods.

## Why It Matters
By grouping related input, clarification, and output events under a common session_id, this module provides temporal structure to otherwise fragmented data. Sessionization is essential for replayability, caregiver context reconstruction, and understanding behavior over time. It also supports compliance, audit, and training workflows.

## Responsibilities
- Generate globally unique session_id values for each new interaction window per user.
- Define and manage session lifecycle, including start, end, and timeout policies.
- Track session start and end events with associated metadata.
- Tag all CARE-related messages (A3CPMessage, clarifications, outputs) with the active session_id.
- Maintain a chronological timeline of all events linked to each session.
- Persist session metadata durably for audit, debugging, and training workflows.

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
