# Module: confidence_evaluator

## Purpose
Computes weighted confidence scores for each candidate intent using classifier predictions, user memory, and contextual relevance.

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

## CARE Integration
- **Upstream**: Receives inputs from the Input Broker and Context Profiler
- **Downstream**: Sends ranked intent list to Clarification Planner or Output Planner
- **Logging**: Scores and inputs are written to inference trace log for transparency
- **Memory Fusion**: Integrates recent user data to personalize output scoring

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

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
