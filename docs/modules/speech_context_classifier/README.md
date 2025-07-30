# Module: speech_context_classifier

## Purpose
Classifies partner speech against the user’s known intent vocabulary by computing the most likely referred intents using semantic inference. This is performed via a constrained large language model (LLM) that ranks candidate intents based on contextual alignment and example match. The module does not infer dialog acts, prompt types, or clarification needs. It enables downstream decision making by producing a relevance-ranked list of known user intents.

| Field                  | Value                                              |
|------------------------|----------------------------------------------------|
| **Module Name**        | `speech_context_classifier`                        |
| **Module Type**        | `classifier`                                       |
| **Inputs From**        | `speech_transcriber`, `user_profile_store`        |
| **Outputs To**         | `input_broker`                                     |
| **Produces A3CPMessage?** | ✅ Yes (classifier_output only)                 |

## Why It Matters
Partner speech often implicitly signals which user intents are being prompted, but those signals are often indirect, idiomatic, or context-sensitive. By leveraging an LLM constrained to the user's trained vocabulary, this module enables robust and flexible intent inference while keeping classification bounded, interpretable, and fast enough for real-time systems.

## Responsibilities
- Receive live or batch transcript segments from `speech_transcriber`
- Look up user-specific mappings (gesture, vocalization) from `user_profile_store`
- Use LLM to semantically match partner utterance to user-known intents:
  - Intents are described by their `label`, `modality`, and `examples`
  - LLM is prompted to select the most likely labels with justification
- Return top N (e.g. 3) highest scoring intent matches
- Output only match scores; downstream modules determine clarification

## Not Responsible For
- Inferring dialog acts or prompt types (e.g., questions, commands)
- Determining if clarification is needed
- Generating clarification prompts
- Maintaining long-term session history
- Translating or rephrasing utterances

## Inputs
- Transcripts from `speech_transcriber`
- Session/user metadata:
  - `timestamp`, `session_id`, `user_id`
- `vocabulary` list from `user_profile_store`:
  - Each item includes `label`, `modality`, and `examples`
  - These constrain and guide the LLM's reasoning

## Outputs
- Structured output object:
  - `matched_intents`: List of intent labels ordered by inferred relevance
  - `relevance_scores`: Dict of intent → normalized score (0.0–1.0)
  - `flags`: Optional markers such as `partner_engaged`, `topic_shift` (but not `needs_clarification`)

{
  "schema_version": "1.0.0",
  "record_id": "uuid4-here",
  "user_id": "elias01",
  "session_id": "sess_2025-07-01_elias01",
  "timestamp": "2025-07-01T13:24:58.321Z",
  "modality": "speech",
  "source": "caregiver",
  "classifier_output": {
    "intent": "drink",
    "confidence": 0.83,
    "ranking": [
      { "intent": "drink", "confidence": 0.83 },
      { "intent": "eat",   "confidence": 0.75 },
      { "intent": "rest",  "confidence": 0.42 }
    ],
    "flags": {
      "partner_engaged": true,
      "topic_shift": false
    }
  }
}


## CARE Integration
Acts as a scoped semantic classifier providing candidate intents for rule-based filtering in the `confidence_evaluator`. It supplies LLM-derived match confidence while ensuring that inference stays within the bounds of the user’s declared intent space.

## Functional Requirements
- F1. Accept single or batch partner utterances
- F2. Retrieve and cache user vocabulary (intent + examples)
- F3. Construct and send constrained LLM prompt with utterance + vocabulary
- F4. Parse and normalize scores for top-N matched intents
- F5. Output results without performing clarification logic

## Non-Functional Requirements
- NF1. Must complete inference in <200ms per utterance when accelerated (fallback allowed)
- NF2. Must support multilingual input and example matching
- NF3. Must degrade gracefully if vocabulary is empty
- NF4. Output must conform to schema and be logged for audit/training
- NF5. Must preserve user intent boundaries (no open intent generation)

## Developer(s)
Unassigned

## Priority
High

-------------------------------------------------------------------------------
✅ SCHEMA COMPLIANCE SUMMARY
-------------------------------------------------------------------------------

This module emits partial `A3CPMessage` records with a `classifier_output` object.

Populated fields:
- `modality = "speech"`, `source = "caregiver"`
- `classifier_output.intent`: Top-ranked matched intent label
- `classifier_output.confidence`: Normalized confidence score
Optional:
- `classifier_output.ranking`: List of top-N matched labels
- `classifier_output.flags`: e.g., `partner_engaged`, `topic_shift`

These records are passed to `input_broker` for multimodal fusion.

## Example Files
- `examples/transcript_input.json`
- `examples/context_output_with_matches.json`
- `examples/context_output_empty.json`
