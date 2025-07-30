# Module: confidence_evaluator

## Purpose
Computes weighted confidence scores for each candidate intent using classifier predictions, user memory, and contextual relevance.

| Field                  | Value                                                              |
|------------------------|--------------------------------------------------------------------|
| **Module Name**        | `confidence_evaluator`                                             |
| **Module Type**        | `coordinator`                                                      |
| **Inputs From**        | `input_broker`, `memory_integrator`                                |
| **Outputs To**         | `clarification_planner`                         |
| **Produces A3CPMessage?** | ✅ Yes (updated `classifier_output`, optional `final_decision`) |


## Why It Matters
The Confidence Evaluator ensures that system decisions reflect not only raw classifier outputs but also user-specific history and situational context. By integrating memory frequency and contextual alignment, it improves the prioritization of correct interpretations and builds trust in system behavior.

## Responsibilities
- Aggregate inputs from classifier output, memory, and contextual priors
- Compute weighted scores for each candidate intent
- Return a ranked list of intents for downstream planners
- Log scoring breakdowns for transparency and audit

## Not Responsible For
- Prompting the user or triggering clarifications
- Rendering outputs or making final decisions
- Executing language models or deep memory integration
- Managing session control or user interface

## Inputs
- `classifier_output`: Raw intent predictions with base confidence scores
- `memory.intent_boosts`: Scores derived from user-specific memory (e.g., frequency, recency)
- `context.topic_tag`: Topic or domain relevance for current interaction
- `context.relevance_score`: Quantitative context alignment metric
- `user_id`, `session_id`, `timestamp`: Provenance metadata

## Outputs
- `classifier_output`: Ranked candidate intents with final weighted scores
- `context.flags`: Updated context or decision flags (optional)
- `final_decision` (optional): Only if a threshold or single dominant intent is confidently selected
- `timestamp`: Time of decision
- Structured audit log entry capturing all score components




{
  "schema_version": "1.0.0",
  "record_id": "uuid4-here",
  "user_id": "elias01",
  "session_id": "sess_2025-07-01_elias01",
  "timestamp": "2025-07-01T13:35:14.382Z",
  "modality": "gesture",
  "source": "communicator",
  "classifier_output": {
    "intent": "drink",
    "confidence": 0.91,
    "ranking": [
      { "intent": "drink", "confidence": 0.91 },
      { "intent": "eat",   "confidence": 0.72 },
      { "intent": "rest",  "confidence": 0.43 }
    ]
  },
  "context": {
    "flags": {
      "ambiguous_intent": false
    }
  },
  "final_decision": "drink"
}


## CARE Integration

- **Upstream**: Receives aligned multimodal `A3CPMessage` records from `input_broker` and memory/context boosts from `memory_integrator`
- **Downstream**: Sends scored output to `clarification_planner`, which decides whether clarification is needed or passes it on to `output_expander`
- **Fusion Role**: Combines classifier, context, and memory signals into a single weighted interpretation
- **Logging**: (Optional) All scoring inputs and decisions are stored in `inference_trace.jsonl` for auditability

## Functional Requirements
- F1. Must compute weighted scores using classifier output, memory frequency, and context alignment
- F2. Must support per-user memory input integration
- F3. Must allow configuration of scoring weights via external settings or API

## Non-Functional Requirements
- NF1. Must return scores in under 50ms per inference request
- NF2. Must allow dynamic hot-swapping of scoring algorithms (e.g., via plug-in or config)
- NF3. Must log each score component and decision basis for audit

## Developer(s)
Unassigned

## Priority
High
-------------------------------------------------------------------------------
✅ SCHEMA COMPLIANCE SUMMARY
-------------------------------------------------------------------------------

This module emits updated `A3CPMessage` records with:

- `classifier_output.intent`: Re-ranked top intent
- `classifier_output.confidence`: Final weighted score
- `classifier_output.ranking`: Updated list of candidate intents with scores
- `context.flags`: Optional updated tags (e.g., `ambiguous_intent`)
- `final_decision`: Only if a threshold or override condition is met
- All original metadata (`timestamp`, `modality`, `user_id`, etc.) preserved

Modifies only the interpretation and scoring fields; does not alter signal provenance.


## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
