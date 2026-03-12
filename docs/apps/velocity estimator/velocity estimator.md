# Solo Development Velocity Rubric

This rubric estimates **effort in points** for a development slice or day.
It is calibrated for **solo system architecture and deep engineering work**.

**Planning rule**

estimated_dev_days = total_points / 10

(≈10 points represents a typical full development day)

---

# Effort Categories

| Category | Small | Medium | Large |
|----------|------:|-------:|------:|
| Feature | 3 | 5 | 8 |
| Refactor | 2 | 4 | 6 |
| Tests | 1 | 2 | 4 |
| Docs | 1 | 2 | 3 |
| Infrastructure | 2 | 4 | 6 |
| Security | 2 | 4 | 6 |
| Bugfix | 1 | 2 | 4 |
| Investigation / Stabilization | 2 | 5 | 8 |
| Meta (planning / tooling) | 1 | 2 | 3 |

---

# Scoring Rules

- Score **work slices**, not commits.
- Use **1–3 dominant categories**.
- Prefer **medium** unless clearly trivial or complex.
- Maximum score per slice/day: **16 points**.
- If debugging, failure analysis, or system stabilization occurred, include **Investigation / Stabilization**.

---

# Point Interpretation

| Points | Typical Effort |
|------:|----------------|
| 1–3 | trivial adjustment (<0.5 day) |
| 4–7 | small feature or refactor (~0.5–1 day) |
| 8–10 | solid development day |
| 11–13 | heavy engineering day |
| 14–16 | major architecture or integration day |

---

# Example Scoring

**Architectural Refactor Day**

Refactor (large) + Tests (medium) + Docs (small)

6 + 2 + 1 = **9 points**

≈ one solid development day.

---

**Integration / Stabilization Day**

Feature (medium) + Refactor (large) + Tests (medium) + Investigation (small)

5 + 6 + 2 + 2 = **15 points**

≈ major development day.

---

# Practical Estimation Workflow

1. Score each **planned development slice**.
2. Sum total points.
3. Estimate duration using:

estimated_dev_days = total_points / 10

Using **10 points/day** keeps estimates conservative and realistic for solo deep-engineering work.
