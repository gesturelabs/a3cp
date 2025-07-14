# Module: memory_interface

## Purpose
The `memory_interface` module maintains lightweight, per-user interaction memory including past intents, confirmation outcomes, and clarification decisions. It provides personalized scoring hints and fallback intent suggestions to improve reliability and reduce repeated misunderstandings.

## Why It Matters
Without memory, the system treats every interaction as isolated. By remembering what worked (or failed) in previous sessions, the system can adapt its confidence scoring, reduce ambiguity, and personalize behavior—especially important for users with consistent communication patterns.

## Responsibilities
- Store intent labels, outcomes (confirmed/rejected), and clarification results per user.
- Track interaction frequency and recency for each intent.
- Compute ranking modifiers (e.g., `intent_boosts`) used by `memory_integrator`.
- Provide fallback suggestions for low-confidence situations (e.g., “often chosen intents”).
- Persist memory data across sessions in a schema-compliant, append-only format.
- Support queries from CARE Engine or `memory_integrator`.

## Not Responsible For
- Modifying intent scores or making final decisions (handled by `memory_integrator`).
- UI rendering or clarification prompt generation.
- Direct session state modification.
- Performing statistical analytics or model-based prediction on memory data.

## Inputs
- `user_id`, `session_id`, `timestamp`
- `intent_label`, `label_status` (e.g., "confirmed", "rejected", "corrected")
- `final_decision` (optional)

## Outputs
- `memory.intent_boosts`: dict of adjusted confidence hints per intent.
- `memory.fallback_suggestions`: ranked list of intents that could be used when confidence is low.
- `final_decision`: echoed for logging context.
- Memory audit log entry (structured JSON, readonly unless explicitly updated).

## CARE Integration
- **Feeds**: `memory_integrator`, `clarification_planner`
- **Triggered by**: Classifier result confirmation, clarification outcomes
- **Supports**: Intent reweighting, fallback prioritization
- **Does not**: Perform scoring or inference directly

## Functional Requirements
- F1. Store intent interactions, confirmation outcomes, and clarification resolutions per user.
- F2. Track intent recency, frequency, and correctness.
- F3. Provide confidence bias modifiers (`intent_boosts`) per intent on request.
- F4. Offer fallback suggestions based on interaction patterns.
- F5. Persist all data using embedded SQLite or memory-backed store with autosave.

## Non-Functional Requirements
- NF1. All memory queries must return in <100ms to avoid CARE Engine latency.
- NF2. All records must be isolated per pseudonym to preserve data privacy.
- NF3. Memory must persist across sessions and survive soft restarts.
- NF4. Module must expose a read-only mode for inference-only environments (e.g., live deployment).
- NF5. All updates must be append-only and validated against a schema for auditability and traceability.

## Developer(s)
Unassigned

## Priority
High – required for memory-based adaptation and auditability.

## Example Files
- [memory_store.db] – autosaved SQLite file (embedded)
- [sample_memory_entry.json](./sample_memory_entry.json)
- [memory_audit_log.jsonl](./memory_audit_log.jsonl)

## Open Questions
- What retention policy should be applied (e.g., age-based, capped history)?
- Should memory records include context tags (e.g., location, partner_speech)?
- How are correction histories weighted relative to frequency/recency?
- What fallback strategy is used when memory is incomplete: default priors or backup classifiers?
