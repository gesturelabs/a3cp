# Module: memory_integrator

## Purpose
The `memory_integrator` module personalizes intent inference by modifying candidate intent scores based on the user's interaction history. It uses features like recency, frequency, and correction logs to reweight classifier outputs before a final decision or clarification.

## Why It Matters
By incorporating learned patterns from past interactions, the system becomes more accurate, efficient, and user-adaptive. This helps minimize repeated misunderstandings, reduces clarification frequency, and supports adaptive learning over time for each individual user.

## Responsibilities
- Retrieve user-specific memory traces, including:
  - Intent usage frequency
  - Recency of use
  - History of manual corrections or clarifications
- Apply memory-informed modifiers to incoming classifier outputs.
- Adjust or re-rank the list of intent candidates accordingly.
- Log the use of memory-based hints for transparency, auditability, and retraining.

## Not Responsible For
- Initial classification or scoring (done by Confidence Evaluator).
- Storing or updating user memory records (handled by Memory Store).
- Making final clarification or rendering decisions.
- Generating natural language prompts or UI responses.

## Inputs
- `classifier_output`: list of intent candidates with base scores.
- `memory.intent_boosts`: prior-weighted modifiers derived from user memory (e.g., boost recent or frequent intents).
- `memory.hint_used`: binary or categorical flags indicating use of memory features.
- `user_id`, `session_id`, `timestamp`.

## Outputs
- `classifier_output`: re-ranked or score-modified list of intent candidates.
- `memory.hint_used`: updated indicators of memory influence (e.g., `"recency_boosted": true`).
- `final_decision` (optional): top-ranked intent after memory adjustment (may still be passed to Clarification Planner).
- Log entry noting:
  - Original and adjusted scores
  - Memory features applied
  - Traceability to specific memory records used

## CARE Integration
- **Follows**: Confidence Evaluator.
- **Feeds**: Clarification Planner or Output Generator depending on confidence after memory adjustment.
- **Logs for**: Memory reuse audit and retraining dataset.
- **Does not perform**: Classification, fusion, or prompting.

## Functional Requirements
- FR1. Must access and apply per-user memory traces (recency, frequency, correction history).
- FR2. Must re-rank or re-score candidate intents based on memory influence.
- FR3. Must log score modifications and memory hint usage.

## Non-Functional Requirements
- NF1. Must complete within <30ms to avoid interaction delay.
- NF2. Must support both session-local and persistent memory sources.
- NF3. Must handle sparse or missing memory gracefully without errors.
- NF4. Must produce deterministic and explainable outputs for the same memory state and input scores.

## Developer(s)
Unassigned

## Priority
High (core to personalization and CARE learning)

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [memory_trace_example.json](./memory_trace_example.json)

## Open Questions
- Should memory weights be linear (e.g., additive) or nonlinear (e.g., softmax boost)?
- Do we need session-level override or backoff if long-term memory diverges from recent patterns?
- Should corrections from clarification responses have a higher weighting than frequency/recency alone?
- Can this module support online learning from real-time feedback, or is it purely reactive?
