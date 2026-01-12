# EXIT_GATES.md — Pipeline Readiness Gates

This document defines **cross-module exit gates** for the A3CP pipeline.
Exit gates are **readiness criteria**, not module TODOs.

They mark the point at which one stage of the pipeline is considered
*stable, reproducible, and safe* to hand off to the next stage.

Exit gates span multiple modules and runtime concerns and therefore
**must not live inside individual app TODOs**.

---

## Exit Gate — Gesture Features “Ready to Classify”

This gate must pass **before enabling or wiring any gesture classification module**.

Scope:
- landmark_extractor (artifact production)
- schema_recorder (session JSONL semantics)
- storage + runtime environment
- replay behavior under identical build/container tags

### Artifact integrity & loadability
For a completed session, the system can reliably:

- [ ] Load the landmark feature artifact by `record_id`
      using `raw_features_ref.uri`
- [ ] Recompute and verify integrity:
      `sha256 == raw_features_ref.hash`
- [ ] Load the feature array and confirm shape `(T, D)`
- [ ] Verify `D == raw_features_ref.dims`

### Replay & determinism guarantees
- [ ] After a service restart **using the same build/container tag**,
      replaying the same `record_id` produces:
  - identical bytes
  - the same `sha256`
- [ ] Determinism is **not** required across different builds or container tags

### Session log semantics
- [ ] Session JSONL contains **exactly one**
      landmark feature-ref schema event per bounded capture (`record_id`)
- [ ] Duplicate or replayed appends for the same capture are prevented
      or handled idempotently per recorder policy

---

## Ownership & enforcement notes

- This exit gate is **evaluated across modules**.
- No single module fully owns these guarantees.
- Modules must **support** this gate but should not duplicate it.

Recommended references (one-line only):
- `landmark_extractor/TODO.md`:
  > Must satisfy Gesture Feature Exit Gate (EXIT_GATES.md)
- `schema_recorder/TODO.md`:
  > Recorder semantics must support Gesture Feature Exit Gate

---

## Status

- Gates are **design constraints**, not implementation steps.
- A gate is considered *passed* only when all checks are verifiably satisfied
  under the defined runtime conditions.
