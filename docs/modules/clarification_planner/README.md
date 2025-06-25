# Module: clarification_planner

## Purpose
Determines whether to trigger a clarification prompt based on confidence levels and ambiguity in predicted user intents.

## Why It Matters
The Clarification Planner ensures transparent and accurate communication by detecting uncertainty in multimodal inference results. It improves robustness by prompting the system to ask for clarification when predictions are ambiguous, low-confidence, or potentially incorrect.

## Responsibilities
- Evaluate classifier outputs for confidence and ambiguity
- Apply configurable thresholds to trigger clarification decisions
- Detect tie scores or unclear top-ranked intent candidates
- Generate metadata payload for use by the LLM Clarifier
- Log clarification decisions with reasoning for auditability
- Optionally emit override recommendations (`final_decision`)

## Not Responsible For
- Running inference (e.g., gesture, audio, context classifiers)
- Fusing multimodal inputs into classifier outputs
- Rendering UI prompts or interacting with end users
- Training or updating underlying models

## Inputs
- `classifier_output`: Ranked list of intent candidates with confidence scores
- `context.flags`: Flags set by contextual modules
- `context.topic_tag`: Topic-level metadata
- `context.relevance_score`: Relevance metric, if available
- `user_id`, `session_id`, `timestamp`: Provenance metadata
- Optional: Memory features such as unresolved intents or recent predictions

## Outputs
- `clarification_trigger`: Boolean indicating whether to ask for clarification
- `clarification_payload`: Optional metadata for LLM Clarifier (if triggered)
- `audit_log`: Justification and metadata for the decision
- Optional: `final_decision_override` recommendation

## CARE Integration
- **Upstream**: Receives inference results and context from Confidence Evaluator and memory modules
- **Downstream**: Triggers LLM Clarifier when clarification is needed
- **Logged**: Emits structured decision entries to `inference_trace.jsonl` or audit logs
- **Decision Node**: Governs whether user interaction is required before committing to an intent

## Functional Requirements
- F1. Must apply configurable confidence and ambiguity thresholds to each prediction
- F2. Must detect tie scores or multiple unclear top-ranked intents
- F3. Must construct clarification metadata payload for LLM Clarifier
- F4. Must emit a clarification trigger boolean in <30ms

## Non-Functional Requirements
- NF1. Must log all trigger decisions with reasoning for audit
- NF2. Must allow runtime tuning of thresholds via config
- NF3. Should complete decisions in under 30ms to avoid UX latency

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
