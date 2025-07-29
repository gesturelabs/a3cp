# Module: session_manager

## Purpose
The `session_manager` module organizes all user interactions into discrete, timestamped sessions. It assigns and tracks session identifiers, enabling linked logs for audit, caregiver review, debugging, and the construction of training datasets over coherent interaction periods.

## Why It Matters
By grouping related input, clarification, and output events under a common `session_id`, this module provides temporal structure to otherwise fragmented data. Sessionization is essential for replayability, caregiver context reconstruction, and understanding behavior over time. It also supports compliance, audit, and training workflows.

## Responsibilities
- Generate unique session IDs for each new interaction window
- Track session start and end events with associated metadata
- Tag all CARE-related messages with the active `session_id`
- Maintain a chronological timeline of session-linked events
- Support export or review of complete sessions (e.g., JSON bundle, timeline view)

## Not Responsible For
- Performing inference, classification, or clarification logic
- Storing raw media, video, or audio files
- Making decisions about label correctness or clarification validity

## Inputs
- Interaction metadata:
  - `timestamp`, `user_id`, `modality`
  - `context.partner_speech`, `context.session_notes`
- CARE Engine messages:
  - `classifier_output`, `final_decision`, `output_phrase`
- Session event messages:
  - session_id, timestamp, user_id
  - The session phase (start or end) is determined by internal logic, not by schema
## Outputs
- Structured session metadata logs:
  - `session_id`, `user_id`, `start_time`, `end_time`
- Annotated `A3CPMessage` records with session tags
- Chronological interaction bundles grouped by session
- Optional summary or session index for review interfaces

## CARE Integration
The `session_manager` wraps all CARE Engine input/output events into cohesive sessions. It ensures that every `A3CPMessage` logged by the system includes a `session_id`, allowing downstream modules (e.g., clarification, caregiver tools, retraining pipelines) to access a consistent timeline of related interactions. This module does not alter or classify messages. It assigns session_id values, records start/end markers, and links events chronologically for downstream consumption.

## Functional Requirements
- F1. Must generate unique `session_id` values per user per session
- F2. Must track and log session boundary events (start/end) using standardized SessionEvent payloads; classification of boundary is performed internally
- F3. Must tag every `A3CPMessage`, clarification, and output with the correct `session_id`
- F4. Must support chronological export or replay of all session-linked events
- F5. Must record session notes and context when available

## Non-Functional Requirements
- NF1. Session tracking must persist across temporary network disconnects
- NF2. Latency for session tagging must remain <10ms per message
- NF3. Session logs must be append-only and audit-compliant
- NF4. Session IDs must remain stable and globally unique
- NF5. Module must support timeout- or user-driven session termination

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [session_manager_input_example.json](./session_manager_input_example.json)
- [session_manager_output_example.json](./session_manager_output_example.json)
- [session_manager_schema.json](./session_manager_schema.json)
