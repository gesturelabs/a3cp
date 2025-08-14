Schema Import Refactor Plan
===========================
### policy and rational
Objectives
----------
1. Single public surface for schemas: from schemas import <Module>Input, <Module>Output only.
2. Stable aliasing in schemas/__init__.py for all route-facing names.
3. Correct example methods: inputs have example_input(), outputs have example_output().
4. Generator/test alignment with new pattern.
5. Guardrails: tests fail on submodule imports and missing aliases.

Steps
-----
0. Pre-flight tidy:
   - Remove .DS_Store etc. from repo.
   - Confirm one-file-per-module convention holds.

1. Define public API in schemas/__init__.py:
   - Explicitly re-export for each module.
   - Map internal class names → <Module>Input / <Module>Output.
   - Example:
     from .audio_feed_worker.audio_feed_worker import (
         AudioFeedWorkerConfig as AudioFeedWorkerInput,
         AudioChunkMetadata as AudioFeedWorkerOutput,
     )
     __all__ = ["AudioFeedWorkerInput", "AudioFeedWorkerOutput", ...]

2. Fix example methods per model:
   - Only input models have example_input().
   - Only output models have example_output().
   - Move misplaced example_input() from outputs to inputs.

3. Update routes gradually:
   - Change imports from "schemas.<mod>.<file>" to "from schemas import <Module>Input, <Module>Output".
   - Do one route at a time; commit after each.

4. Keep generator aligned:
   - Generator should import internal module files, not public schemas package.
   - Avoid relying on __all__ for generation.

5. Add guardrail tests:
   - Test 1: fail if any route imports "schemas.<submodule>".
   - Test 2: ensure each module's <Module>Input/Output appears in schemas.__all__.

6. Wire into CI:
   - Run guardrail tests in CI workflow.
   - Optionally add Ruff rule for import policy.

7. Document contract:
   - Routes must import only from schemas.
   - Add aliases for new schemas in __init__.py.
   - example_input() lives on inputs, example_output() on outputs.

8. Retire legacy imports:
   - After migration, enable enforcement test in CI.
   - Optionally extend rule to services.

Pitfalls
--------
- Avoid circular imports by keeping __init__.py imports explicit and one-way.
- Do not rename public aliases without deprecation.
- Keep example_* methods in correct class type.
- Prevent shadowing by using unique public aliases.


### ------------------------------
# Per-Module Schema Refactor Workflow (ASCII Plan)
### ------------------------------



## 0) Preconditions
- Confirm module exists in `docs/modules/<module>.md` and `schemas/<module>/<module>.py`.
- Verify generator builds JSON examples from **single** schema file.
- Ensure `api/` boots so regressions are traceable.

---

## 1) Review Module Design Doc
Input: `docs/modules/<module>.md`
Output: Decision note appended to doc:
- Canonical Input/Output names.
- Field list & types (match `SCHEMA_REFERENCE.md`).
- Minimal examples (map to `example_*()` later).

**Gate A — Design Check**
- Input/Output clear.
- No naming collisions.
- IDs/timestamps follow conventions.

---

## 2) Review Legacy Schema File
Input: `schemas/<module>/<module>.py`
Check:
- Which classes are inputs vs outputs.
- Location of `example_*()` methods.
- Internal helper types used by generator.
- Generator import path compatibility.

**Gate B — Generator Compatibility**
- Single file remains source.
- Renames planned but deferred.

---

## 3) Update API Routing (structure only)
Inputs:
- `api/main.py`
- `api/__init__.py`
- `api/routes/<module>_routes.py`

Tasks:
- One router file per module.
- Route paths follow `/module/verb.noun`.
- Router prefix/tags match namespace.

**Gate C — API Namespace Check**
- Swagger routes appear once.
- No duplicate mountings/prefixes.

---

## 4) Build `apps/<module>` Scaffold
Purpose: business logic stubs; keep route files thin.
Output: skeleton wired by routes, using old schema imports.

**Gate D — Execution Check**
- `uvicorn` runs.
- Route accepts request, returns placeholder.

---

## 5) Public Schema Surface Planning
Decide:
- Public alias names: `<Module>Input`, `<Module>Output` (or Start/End variants).
- Map legacy class names → public aliases.
- Any temporary deprecations to keep old imports alive.

**Gate E — Alias Map Approved**
- Aliases unique.
- No circular import risk.

---

## 6) Guardrail Test Plan (scoped)
Draft:
- Test 1: No deep schema imports in routes.
- Test 2: Public aliases in `schemas.__all__`.

**Gate F — Test Scope Agreed**
- Scope limited to this module for now.

---

## 7) Execute Schema Refactor (single commit)
- Move `example_*()` to correct classes in `schemas/<module>/<module>.py`.
- Add public aliases in `schemas/__init__.py` (explicit, in `__all__`).
- Update router imports to use `from schemas import ...`.
- Keep generator pointing to internal file.

**Gate G — Green Build**
- Routes serialize with public models.
- Generator succeeds.
- Tests for module pass.

---

## 8) Add Guardrail Tests & CI Wiring
- Implement two tests for this module.
- Add to CI; failures are actionable.

**Gate H — CI Green**
- CI enforces contract for this module.

---

## 9) Document & Finalize
- Update `docs/CHANGELOG.md`.
- Update `SCHEMA_REFERENCE.md` if needed.
- Add CONTRIBUTING note: “Routes import only from `schemas`.”

**Gate I — Definition of Done**
- Public aliases stable & documented.
- Generator deterministic.
- No deep imports in routes.
- Tests & CI enforce contract.

---

## Roll-Forward Strategy
1. Repeat steps 1–9 per module.
2. Widen guardrail test path after ≥3 modules migrated.
3. After all migrated, enforce project-wide guardrails and drop legacy allowances.

---

## Risk Controls
- Old code remains generator source until module passes all gates.
- Public aliasing added last.
- Guardrail tests start scoped.
- One module at a time for safe rollback.
