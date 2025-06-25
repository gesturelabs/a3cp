# Module: llm_clarifier

## Purpose
The `llm_clarifier` module generates natural language clarification prompts when the CARE Engine detects ambiguity or low confidence in inferred user intent. It serves as a fallback mechanism to resolve uncertainty by asking the user or caregiver directly.

## Why It Matters
Clarification is essential for accuracy and trust. By leveraging lightweight local LLMs, this module enables the system to engage in understandable, context-aware dialog without relying on remote APIs or heavy infrastructure. It also collects human-in-the-loop corrections for retraining and audit.

## Responsibilities
- Accept structured input from the CARE Engine, including:
  - Ranked intent candidates
  - Confidence scores
  - Contextual metadata and topic flags
- Use a local quantized LLM (e.g., Mistral, Phi, Bloom via GGUF) to generate:
  - A clear natural language prompt (e.g., “Did you mean eat or help?”)
  - Optional metadata (e.g., top candidate intents, flags used)
- Return a prompt string that can be shown in the UI.
- Log the prompt and user response to `training_feedback.jsonl` for future model improvement.

## Not Responsible For
- Deciding *when* to trigger clarification (handled by Clarification Planner).
- Presenting UI elements or collecting responses.
- Final classification decisions or retraining.
- Managing session state or memory.

## Inputs
- `classifier_output`: ranked list of intent candidates with confidence scores.
- `context.topic_tag`: thematic context (e.g., meal, help, object).
- `context.flags`: CARE Engine internal markers (e.g., `low_confidence`, `ambiguous_gesture`).
- `user_id`, `session_id`, `timestamp`.

## Outputs
- `output_phrase`: clarification prompt string (e.g., “Did you mean help or play?”).
- `output_mode`: prompt type (`multiple_choice`, `open_ended`, `yes_no`, etc.).
- `context.flags`: carried forward or updated.
- Log entry to `training_feedback.jsonl` containing:
  - CARE input summary
  - Generated prompt
  - User or caregiver response (if collected downstream)

## CARE Integration
- **Triggered by**: Clarification Planner inside the CARE Engine.
- **Feeds**: UI module that presents clarification prompt.
- **Logs for**: Memory-based learning and CARE feedback loop.
- **Does not perform**: Fusion, classification, or user interface tasks directly.

## Functional Requirements
- F1. Must accept structured input from the CARE Engine summarizing ambiguity.
- F2. Must generate one or more clarification prompts using a small LLM.
- F3. Must return a clear, context-aware prompt as a string.
- F4. Must support various prompt types: multiple choice, open-ended, binary.

## Non-Functional Requirements
- NF1. Must return a result in <500ms for responsive UX.
- NF2. Must operate offline using quantized GGUF models.
- NF3. Must produce schema-compliant, UTF-8 safe outputs.
- NF4. Must be stateless and sandboxed to isolate LLM execution.
- NF5. Must gracefully handle edge cases (e.g., empty candidate list, poor confidence spread).

## Developer(s)
Unassigned

## Priority
Medium to High (Fallback path critical for ambiguity resolution)

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [training_feedback.jsonl](./training_feedback.jsonl)

## Open Questions
- Should the prompt include multimodal indicators (e.g., gesture + audio cues)?
- Do we allow dynamic rephrasing based on session history or user preferences?
- What UI modules will handle user response capture and validation?
- Is confidence spread or entropy a better trigger threshold than hard cutoff?
