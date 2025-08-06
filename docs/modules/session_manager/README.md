# Module: session_manager

## Purpose
The session_manager module organizes all user interactions into discrete, timestamped sessions. It assigns and tracks session identifiers, enabling linked logs for audit, caregiver review, debugging, and the construction of training datasets over coherent interaction periods.

## Why It Matters
By grouping related input, clarification, and output events under a common session_id, this module provides temporal structure to otherwise fragmented data. Sessionization is essential for replayability, caregiver context reconstruction, and understanding behavior over time. It also supports compliance, audit, and training workflows.

## Responsibilities
- Generate globally unique session_id values for each new interaction window per user.
- Define and manage session lifecycle, including start, end, and timeout policies.
- Track session start and end events with associated metadata, including timestamps and context.
- Tag every CARE-related message (A3CPMessage, clarifications, outputs) with the current session_id.
- Maintain a chronological timeline of all events linked to each session.
- Support export or review of complete session data (e.g., JSON bundles, timeline views).
- Persist session metadata durably to support audit, debugging, and training dataset construction.

## Not Responsible For
- Performing inference, classification, or clarification logic.
- Storing raw media, video, or audio files.
- Making decisions about label correctness or clarification validity.

## Inputs
- Input sources:
  - UI interactions initiating or modifying sessions
  - Direct user inputs and actions
  - Updates or context from user_profile_store

- Data fields received conform to the canonical A3CPMessage schema, including but not limited to:
  - schema_version (e.g., "1.0.1")
  - record_id (UUID for the input event)
  - user_id (pseudonymous user identifier)
  - timestamp (ISO 8601 UTC with milliseconds, e.g., "2025-06-15T12:34:56.789Z")
  - performer_id (actor performing the input, e.g., "carer01")
  - Optional contextual fields as available

- Session lifecycle events (start/end) are determined internally by the session_manager, not by explicit schema fields.

- The input payload example aligns with the BaseSchema’s example_input method.


## Outputs
- Structured session metadata logs capturing:
  - session_id (globally unique session identifier)
  - user_id (pseudonymous user ID)
  - start_time and end_time (ISO 8601 UTC timestamps)
  - session status flags (e.g., active, paused, closed)

- Annotated A3CPMessage records:
  - Every message related to user interaction is tagged with the active session_id for traceability.
  - Messages include contextual metadata as passed through or enriched by session_manager.

- Chronologically ordered bundles of interaction events:
  - Complete sequences of user, caregiver, and system events grouped by session_id.
  - These bundles support replayability, audit, and training dataset extraction.

- Optional session summaries and indices:
  - Metadata aggregates (e.g., total duration, event counts, notable flags).
  - Session indexes to facilitate efficient search and review in caregiver or analyst interfaces.

- Export formats may include:
  - JSONL logs for append-only audit trails.
  - Bundled JSON objects for UI timelines or offline analysis.

## CARE Integration
The session_manager module encapsulates all CARE Engine input/output events into cohesive sessions. It ensures every logged A3CPMessage includes a session_id, providing a consistent, linked timeline accessible to downstream modules such as clarification planners, caregiver tools, and retraining pipelines. The module strictly assigns session identifiers and logs boundaries without altering message content or performing classification.

## Functional Requirements
- F1. Generate unique, stable session_ids per user per session.
- F2. Detect and log session boundaries (start/end) with standardized session event payloads.
- F3. Tag all CARE-related messages consistently with the active session_id.
- F4. Support chronological export and replay of full session event streams.
- F5. Record session notes and contextual metadata when available.

## Non-Functional Requirements
- NF1. Persist session tracking reliably across temporary network disconnects or system restarts.
- NF2. Maintain low latency (<10ms per message) for session tagging operations.
- NF3. Ensure session logs are append-only and compliant with audit policies.
- NF4. Guarantee global uniqueness and stability of session IDs.
- NF5. Support both timeout-driven and user-initiated session termination mechanisms.

## Developer(s)
Unassigned

## Priority
High

## Example Files
- session_manager_input_example.json
- session_manager_output_example.json
- session_manager_schema.json
