# A3CP Gesture Substrate & Personalization Project — Summary

## 1. Goal

Build a reliable gesture recognition system for n=1 sign languages that:

- Detects when an intentional gesture occurs
- Recognizes user-specific gestures from few examples (3 per class)
- Outputs calibrated confidence with conservative reject behavior
- Preserves full auditability and deterministic replay

---

## 2. Architecture

### Universal Model (Shared Substrate)

Trained on multi-person unlabeled data.

Learns:
- Human movement representation (embedding)
- Eventness (gesture vs background)
- Robustness to noise, occlusion, fps variation
- Stable similarity space for few-shot personalization

Outputs per window:
- Embedding vector
- Eventness score
- Quality score

---

### Per-User Layer

Trained on:
- 3 samples per class (10–30 classes)
- Background movement from same user

Implements:
- Class prototypes (embedding averages)
- Cosine similarity scoring
- Threshold + margin reject logic
- Temporal stability gating
- Final distribution including `"unknown"`

---

## 3. Dataset Strategy

### Universal Dataset (Phase 2)

Target:
- 200–500 people
- 30 minutes per person
- ~50–100 hours total
- 20–30% no-action clips

Requirements:
- Boundary annotation (t_start, t_end)
- Diverse camera conditions
- Hard negatives (fidget, reach, self-touch)
- Locked `feature_spec_id`

Avoid:
- Manual video chopping (use metadata slicing)
- Overly scripted identical gestures

---

## 4. Engineering Strategy

### Phase 1 — MVP
- Implement current `gesture_classifier`
- Windowing (16 frames, stride 5)
- Per-user temporal encoder + prototypes
- Deterministic reject logic
- Full inference trace logging

Instrument failure modes:
- Margin, similarity, reject reason
- Quality metrics
- Confusion matrix

Decision point:
- If failures stem from noise/variation → build universal model
- If failures stem from class overlap → refine per-user data

---

### Phase 2 — Universal Encoder
- Self-supervised training (contrastive + masked modeling)
- Use gesture + no-action clips
- Preserve feature spec invariants
- Swap encoder under same classifier contract

Minimal classifier changes required:
- Metadata validation
- FPS handling
- Quality gating

---

## 5. Data Engineering Workload (Realistic)

For ~100 participants:
- Recording: ~60–75 hours
- Annotation: ~10–20 hours
- Cleaning/validation: ~20–40 hours
- Structuring/manifests: ~10–20 hours

Total:
~110–175 hours (~1–2 months part-time)

Mitigation:
- Run pilot (5–10 participants)
- Then delegate as structured student project

---

## 6. Risk Control

Key technical risks:
- False positives in background
- Poor rejection calibration
- Overfitting small per-user data
- Inconsistent boundary annotation

Key mitigation:
- 20–30% no-action data
- Background modeling per user
- Conservative thresholds
- Deterministic replay
- Locked feature spec

---

## 7. Strategic Plan

1. Build and test current bounded-capture classifier.
2. Instrument and evaluate real failure patterns.
3. If robustness insufficient, invest in universal dataset.
4. Delegate structured data pipeline to student once protocol is frozen.
5. Keep encoder pluggable and artifact-versioned.

---

## Core Principle

Shared model learns **movement structure**.
Per-user layer learns **meaning**.
Confidence must be conservative and reproducible.
