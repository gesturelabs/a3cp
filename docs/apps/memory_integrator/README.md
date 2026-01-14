# Module: memory_integrator

## Purpose
The `memory_integrator` module personalizes intent inference by modifying candidate intent scores based on the user's interaction history. It uses features like recency, frequency, and correction logs to reweight classifier outputs before a final decision or clarification. This supports user-adaptive scoring and enhances the CARE Engine’s contextual accuracy by supplementing the `confidence_evaluator` with memory-based weights.


| Field                  | Value                                                                  |
|------------------------|------------------------------------------------------------------------|
| **Module Name**        | `memory_integrator`                                                    |
| **Module Type**        | `coordinator`                                                          |
| **Inputs From**        | `memory_interface`, `confidence_evaluator`                             |
| **Outputs To**         | `confidence_evaluator` (via `memory.intent_boosts`, `memory.hint_used`)|
| **Produces A3CPMessage?** | ❌ No (modifies internal fields used by other modules)              |


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
- `classifier_output`: List of intent candidates with base scores
- `memory_trace`: User-specific memory data retrieved via `memory_interface`, including:
  - `memory.intent_boosts`: Per-label weighting factors
  - `memory.hint_used`: Flags indicating memory strategies applied
- `user_id`, `session_id`, `timestamp`

## Outputs
- Updated `memory.intent_boosts` and `memory.hint_used` fields passed to `confidence_evaluator`
- Log entry capturing:
  - Memory traces used
  - Boosts applied
  - Flags and rationale
- Does **not** emit standalone A3CPMessages


## CARE Integration
- **Upstream**: Pulls memory traces from `memory_interface`
- **Downstream**: Modifies memory-derived weight inputs used by `confidence_evaluator`
- **Logs**: Memory application decisions for retraining and audit
- **Does Not**: Perform classification, prompting, or direct downstream handoff

---

## Output (JSON example)

{
  "memory": {
    "intent_boosts": {
      "go_to_bathroom": 1.3,
      "want_to_eat": 0.9
    },
    "hint_used": {
      "recency_boosted": true,
      "correction_penalty": false
    }
  }
}


## Functional Requirements
-FR1. Must access and apply per-user memory traces (recency, frequency, correction history).
-FR1. Must retrieve per-user memory traces for intent frequency, recency, corrections
-FR2. Must apply scoring modifiers and flags deterministically
-FR3. Must support integration with confidence_evaluator without blocking
-FR4. Must log traceable decision history per input set

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
