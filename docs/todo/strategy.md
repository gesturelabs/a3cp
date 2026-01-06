# A3CP Demonstrator — Revised Strategy & Execution Plan

## Goal
Deliver a **fundable first demonstrator** that proves, end to end:
- real-time operation,
- human-in-the-loop learning,
- persisted, per-user, multimodal models,
- **observable behavior change** after training,
- inspectable session timelines.

The demonstrator optimizes for **credibility and clarity**, not performance.

---

## Core Principles (Non-Negotiable)
- **One vertical loop**, not a broad system.
- **Visible learning > accuracy**.
- **A3CPMessage is the single canonical contract** across all modules.
- **Persist only what proves seriousness**:
  - training examples,
  - model registry metadata,
  - active-model pointers.
- **Multimodal early, shallow by design** (gesture + sound, minimal fusion).
- **Demo reliability over cleverness**:
  - deterministic baseline,
  - replayable sessions,
  - explicit fallbacks.
- **Hardening, optimization, and cleanup are post-demo concerns**.

---

## Vertical Build Order (Thin Slices)

### 1. Session Manager (Spine Only)
Purpose: provide a stable backbone for everything else.

Scope:
- Start / end session
- Stable `session_id`
- Structured event logging
- Minimal persistence (enough to reload sessions)
- No optimization, no feature expansion

Exit criteria:
- Downstream modules can attach:
  - training examples,
  - model artifacts,
  - inference events.

---

### 2. Training Example Capture (Minimal but Explicit)
Purpose: make learning *demonstrable*.

Must include a **strict feedback protocol**:
- classifier prediction + confidence
- partner action:
  - accept prediction, or
  - correct (choose label)
- optional lightweight context tag
- persisted as a single training row

Constraints:
- Linked to `session_id`, `record_id`, modality
- Enforce `consent_given` / `is_demo`
- No schema sprawl

Outcome:
- A growing, inspectable per-user training set.

---

### 3. Model Registry (Credibility Nucleus)
Purpose: prove persistence and intent to scale.

Responsibilities:
- Store model metadata in DB
- Store artifacts on disk
- Explicit activation per `(user, modality)`
- Deterministic load path for inference

Rules:
- One active model per `(user, modality)`
- Activation is explicit and logged
- Reload survives service restart

---

### 4. Baseline + Trained Classifiers (2 Modalities)
Purpose: guarantee visible behavior change.

Modalities:
- Gesture
- Sound

Baseline behavior (pre-training):
- Deterministic and intentionally weak:
  - seeded random,
  - majority default,
  - or “unknown” below threshold

Post-training behavior:
- Simple, per-user model
- Clearly improves on the same replay input
- Accuracy is irrelevant; *difference* is mandatory

---

### 5. Input Broker + Simple Fusion
Purpose: demonstrate multimodal reasoning without complexity.

Responsibilities:
- Time-window alignment
- Minimal fusion logic
- Confidence computation
- Trigger clarification when confidence is low

No advanced fusion.
No optimization.

---

### 6. Clarification → Feedback → Learning Loop
Purpose: close the loop visibly.

Flow:
1. System outputs prediction + confidence
2. Partner:
   - confirms, or
   - corrects
3. Feedback becomes new training data
4. Model retrains
5. Registry activates new model
6. Next inference behaves differently

All steps logged and inspectable.

---

## Session Manager Refactor Guidance
- **Useful but not critical-path**
- Do only what reduces integration risk:
  - unified router,
  - public schema aliases,
  - routes import only from `schemas`,
  - minimal guardrail tests.
- Defer:
  - cleanup,
  - documentation polish,
  - CI hardening.

---

## Demo Acceptance Criteria (Reality Check)
The demonstrator is credible if you can show:

1. Sessions being created and ended.
2. Training examples being collected via partner feedback.
3. Models being trained and persisted.
4. Models being activated explicitly.
5. Multimodal inference running.
6. **Behavior changing after training** on the same input.
7. **Persistence across restarts** (stop service, restart, behavior remains).
8. A readable session timeline tying everything together.

---

## One-Sentence Summary
**Build the smallest system that can learn from a human in the loop, store that learning, reload it reliably, and behave differently next time — and nothing more.**
