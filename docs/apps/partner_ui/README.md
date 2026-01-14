# Module: partner_ui

## Purpose
The `partner_ui` module renders communicative output, visual feedback, and clarification prompts for human partners (e.g., caregivers, clinicians, family members). It provides a real-time interface for observing user intent, responding to clarification requests, and supplying feedback that can influence system adaptation and retraining.

## Why It Matters
Human partners are an essential part of the communicative loop in AAC systems. By making the user’s inferred intent visible, prompting clarifications, and logging partner input, this module supports transparency, trust, and collaborative interaction—especially in ambiguous or emergent communication contexts.

## Responsibilities
- Render final communicative output (speech, text, symbol) for human partners
- Display live gesture visualizations and audio/speech feedback
- Present clarification prompts and candidate options
- Allow partners to:
  - Confirm or correct inferred intent
  - Submit freeform session notes
  - Flag misunderstandings or training errors
- Route partner input (e.g., corrections, confirmations) to the CARE Engine
- Log partner actions for review, retraining, or audit

## Not Responsible For
- Generating or expanding communicative phrases (`output_expander`)
- Selecting output modality (`output_planner`)
- Making final clarification or labeling decisions
- Performing inference or classification

## Inputs
- `output_phrase` and `output_mode` from `output_planner`
- Render-ready visual data (e.g., gesture traces) from `landmark_visualizer`
- Playback media or cues from `sound_playback`
- Clarification prompts from `llm_clarifier`
- `timestamp`, `user_id`, `session_id`: for logging and interaction tracking

## Outputs
- Partner feedback: label corrections, confirmations, session notes
- Clarification responses (e.g., selected candidate intent)
- Retraining flags or signals for the `retraining_scheduler`
- Updates to `user_profile_store` based on partner configurations or corrections
- Optional return signals to `llm_clarifier` (e.g., clarification skipped or confirmed)
- Session control actions (e.g., signal session start/end to `session_manager`)

## CARE Integration
The `partner_ui` is the primary interface for human partners during and after the CARE loop. It displays the system's communicative output and collects structured and unstructured input from the partner that can guide real-time disambiguation, future retraining, and context modeling.

## Functional Requirements
- F1. Render multimodal output in real time
- F2. Display clarification prompts and allow partner selection
- F3. Accept freeform session notes and structured label corrections
- F4. Route all partner input to appropriate downstream modules
- F5. Timestamp and log all actions for traceability and audit

## Non-Functional Requirements
- NF1. Maintain low-latency rendering (<100ms for updates)
- NF2. Fail gracefully if clarification input is delayed or skipped
- NF3. Ensure all partner actions are logged by `session_id` and `user_id`
- NF4. Provide accessible rendering across devices and display types

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [clarification_prompt.json](./clarification_prompt.json)
- [output_render_event.json](./output_render_event.json)
- [partner_feedback_input.json](./partner_feedback_input.json)
- [schema.json](./schema.json)
