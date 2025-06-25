# Module: feedback_log

## Purpose
Captures caregiver or partner feedback on clarification prompts, including confirmations, corrections, or rejections.

## Why It Matters
This module supports retraining, accountability, and error analysis by logging the outcome of ambiguous or uncertain system outputs. It enables the system to learn from human clarification and correction, preserving context for future model updates or evaluation.

## Responsibilities
- Log all clarification interactions including prompt, response, and final decision
- Store caregiver or partner responses (confirmed, corrected, rejected)
- Tag logs with session metadata (e.g., `session_id`, `user_id`, `timestamp`)
- Ensure append-only write behavior for audit compliance
- Support export in structured formats (e.g., `.jsonl`, database rows)
- Validate log schema before accepting entries

## Not Responsible For
- Rendering UI or initiating interaction
- Generating clarification prompts
- Scoring or classification
- Model training or schema evolution

## Inputs
- `prompt_text`: The clarification message shown to user/caregiver
- `user_response`: Raw or normalized reply (e.g., “yes”, “no”, corrected label)
- `intent_label`: Initial predicted label under review
- `label_correction`: Corrected label if given
- `label_status`: Enum: `confirmed`, `corrected`, or `rejected`
- Metadata: `session_id`, `user_id` or `pseudonym`, `timestamp`
- Optional: `output_mode` (e.g., speech, symbol, text)

## Outputs
- Structured log entries per clarification event:
  - All input fields above
  - Internal `entry_id` (for append-only export tracking)
- Exportable format (e.g., `.jsonl`) for retraining or audit pipelines

## CARE Integration
- **Upstream**: Consumes clarification response payloads from UI or CARE Engine
- **Downstream**: Supplies logs for training systems, audit interfaces, or reviewers
- **Parallel Use**: Supports real-time validation but primarily operates post-decision

## Functional Requirements
- F1. Must log each clarification interaction with prompt, response, and outcome
- F2. Must record caregiver overrides or corrections if provided
- F3. Must tag each entry with session metadata (timestamp, user_id, session_id)

## Non-Functional Requirements
- NF1. Must support append-only logging to ensure audit integrity
- NF2. Must validate schema for each entry before writing
- NF3. Must support export to `.jsonl` or structured audit database

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
