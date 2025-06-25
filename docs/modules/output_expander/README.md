# Module: output_expander

## Purpose
The `output_expander` module transforms confirmed user intents into natural-language phrases tailored to individual preferences, communicative tone, and contextual factors. It serves as the bridge between internal decision-making and human-understandable AAC outputs.

## Why It Matters
This module plays a critical role in the A3CP pipeline by ensuring that final system decisions—such as `"eat"` or `"help"`—are rendered as socially appropriate, clear, and context-sensitive phrases. It directly affects communicative success, caregiver comprehension, and the overall expressiveness of the system for users with complex communication needs.

## Responsibilities
- Convert `final_decision` into an AAC-ready phrase (`output_phrase`)
- Adapt phrasing style based on user profile (e.g., tone: polite, direct, playful)
- Incorporate contextual cues (e.g., `context_location`, `context_partner_speech`) into phrasing templates
- Select or generate natural-language output using templates or prompt-based LLMs
- Return structured output fields: `output_phrase`, `output_mode`, and associated metadata
- Log phrase generation with user/session ID and timestamp for auditing and retraining

## Not Responsible For
- Determining the intent (`final_decision`) itself
- Rendering or speaking the phrase via TTS or symbol boards
- CARE planning, clarification logic, or interactive partner handling
- AAC UI presentation or formatting decisions

## Inputs
- `final_decision`: string (e.g., `"drink"`)
- `user_id`, `session_id`, `timestamp`: core metadata
- `context_*` fields: optional context (e.g., `context_location`, `context_partner_speech`)
- `output_type`: must be `"intent"`
- `user_profile` (from extended schema or internal store): tone or phrasing preferences

## Outputs
- `output_phrase`: string (e.g., `"Can I have a drink?"`)
- `output_mode`: string (e.g., `"speech"`, `"text"`, `"symbol"`)
- Logs: appended `.jsonl` entries with expanded phrase, metadata, and original intent

## CARE Integration
The `output_expander` is triggered after the CARE Engine has resolved the `final_decision`. It is called by the Output Planner to transform the decision into a human-usable communicative phrase. Its output is used by the AAC renderer. Logs are stored under `logs/users/` and `logs/sessions/` for review, audit, and retraining purposes.

## Functional Requirements
- F1. Accept and validate `final_decision`, `user_id`, and `context_*` fields
- F2. Generate natural-language phrase tailored to the intent, tone, and context
- F3. Respect user tone/style preferences (e.g., formal, direct, playful)
- F4. Return valid `output_phrase` and `output_mode` fields for downstream use
- F5. Log expanded phrase with traceable metadata (timestamp, user_id, session_id)

## Non-Functional Requirements
- NF1. Generation time must be <300ms to maintain real-time responsiveness
- NF2. If using LLMs, must operate in sandboxed or rate-limited environment
- NF3. Must fall back to rule-based templates if LLM or external generator fails
- NF4. Outputs must be UTF-8 encoded and safe for text-to-speech rendering
- NF5. User tone/style preferences must persist across sessions and expansions

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
