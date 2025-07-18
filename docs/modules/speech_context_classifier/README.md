# Module: speech_context_classifier

## Purpose
Analyzes transcribed partner speech and session metadata to infer likely communicative context. Narrows the intent space by matching partner prompts to the user's known gesture or vocalization mappings. Provides context priors to the CARE Engine and Clarification Planner.

## Why It Matters
Partner speech often implicitly signals what the user is expected to respond to. By analyzing these signals and intersecting them with the user's trained vocabulary, this module improves efficiency and accuracy in intent classification—reducing unnecessary clarifications and cognitive load.

## Responsibilities
- Receive live or batch transcript segments from `SpeechTranscriber`
- Detect linguistic cues including:
  - Question forms, commands, attention shifts
  - Named entities and topic transitions
- Look up user-specific mappings (gesture, audio) from vocabulary registry
- Match partner prompt content to known mappings using:
  - Lexical matching
  - Semantic similarity (e.g., embedding distance)
- Generate:
  - Relevance scores for matching intents
  - Context flags (e.g., `is_question=True`, `topic='object'`)
- Forward enriched context object to CARE Engine
- Trigger fallback to Clarification Planner if no candidate mapping matches

## Not Responsible For
- Making final intent decisions
- Performing gesture/audio classification
- Maintaining long-term session state (unless configured)

## Inputs
- Transcripts from `SpeechTranscriber`
- Session/user metadata:
  - `timestamp`, `session_id`, `user_id`
- Partner dialog history (`context.partner_speech`)
- User vocabulary registry:
  - List of trained gestures and vocalizations with intent labels

## Outputs
- Structured context object:
  - `prompt_type` (e.g., question, command, unknown)
  - `topic` (e.g., food, help)
  - `matched_intents` (list of known intent labels relevant to current prompt)
  - `relevance_scores` (per intent)
  - `flags` (e.g., `is_question=True`, `needs_clarification=True`)
- If no matches found, sets `context.needs_clarification=True` to guide Clarification Planner

## CARE Integration
Acts as a pre-filter and context provider before CARE Engine intent classification. Narrows the candidate intent space and determines whether clarification is required based on partner prompt relevance to user's known vocabulary.

## Functional Requirements
- F1. Accept transcripts and user/session metadata
- F2. Detect questions, topics, and dialogue act types using rules or LLMs
- F3. Lookup user-specific gesture/audio-intent mappings
- F4. Match prompt content against known intents and compute relevance scores
- F5. Generate and forward structured context object to CARE Engine
- F6. Set `needs_clarification=True` if no viable intent match is found

## Non-Functional Requirements
- NF1. Must complete processing in <200ms per update
- NF2. Must support multilingual transcripts and degraded speech input
- NF3. Must degrade gracefully if user vocabulary is missing or incomplete
- NF4. Output must be schema-compliant and logged for audit/training
- NF5. Must avoid over-restricting the candidate space when uncertain

## Developer(s)
Unassigned

## Priority
High

## Example Files
- `examples/transcript_input.json`
- `examples/context_output_with_matches.json`
- `examples/context_output_needs_clarification.json`
