# Session Manager Refactor — Execution Plan (ASCII)

Goal: Two schemas (`session_manager_start`, `session_manager_end`) exposed via a single public API and a single integrated app/router, with generator + tests aligned.

Repo context (relevant paths):
- Schemas: `schemas/session_manager_start/session_manager_start.py`, `schemas/session_manager_end/session_manager_end.py`
- Routes:  `api/routes/session_manager_start_routes.py`, `api/routes/session_manager_end_routes.py`
- Apps:    `apps/session_manager_start/`, `apps/session_manager_end/`
- Generator: `scripts/generate_schemas_from_master.py` (+ `schema_mapping_config.py`)
- Docs:    `docs/modules/session_manager/README.md`
- Top-level public surface: `schemas/__init__.py`


---

## 0) Pre-flight (tidy + invariants)
[ x] Remove transient files in tree (notably many `.DS_Store` under `/`, `/api`, `/apps`, `/docs`, `/schemas`, `/tests`, `/.github`, `/.ruff_cache`).
[ x] Confirm the invariant: **one Python file per schema module drives generation** (true for session_manager_start/end).
[ x] Ensure `api/main.py` boots (even with stub routes).

**Exit criteria**
- `uvicorn api.main:app` starts without import errors.
- `scripts/generate_schemas_from_master.py` runs without module import failures for session_manager_*.

---

## 1) Documentation baseline (design → contract)
[x ] Review and update `docs/modules/session_manager/README.md` to define:
- Inputs/Outputs for **start** and **end** (names, fields, types).
- Canonical timestamp/ID conventions (match `docs/schemas/SCHEMA_REFERENCE.md`).
- Minimal examples (these will later map to `example_*()` but do **not** change code yet).

**Exit criteria**
- README states the public names we will export: `SessionManagerStartInput/Output`, `SessionManagerEndInput/Output`.

---

## 2) Schema source review (no code changes yet)
[ x] Examine:
- `schemas/session_manager_start/session_manager_start.py`
- `schemas/session_manager_end/session_manager_end.py`

Check:
- Which classes are currently acting as Input vs Output.
- Where `example_input()` / `example_output()` live (note misplacements).
- Any helper types the generator relies on.

**Exit criteria**
- A written mapping: `{internal_class_name} → {public_alias}` for both start/end.

---

## 3) Router normalization (structure only, no behavior redesign)
[x ] Replace dual route files with a **single** `api/routes/session_manager_routes.py` *file name* and plan (do **not** delete old files yet):
- Prefix `/session_manager`, tag `["session_manager"]`.
- Two endpoints: `/sessions.start`, `/sessions.end`.

[x ] Update `api/main.py` to mount **only** the unified router (plan), but keep old imports in place until Step 7 flips consumption to public schemas.

**Exit criteria**
- Swagger shows each endpoint exactly once under `session_manager` after the flip (to be verified in Step 7).

---

## 4) App consolidation plan (no code yet)
[ x] Plan to consolidate `apps/session_manager_start/` and `apps/session_manager_end/` into a single `apps/session_manager/`.
[ x] Decide migration approach:
- **Option A (recommended):** Create `apps/session_manager/` with thin service functions `start_session()` and `end_session()`. Leave old apps in place until new path is wired.
- **Option B:** Keep both old apps; only routes call into a shared façade module. (More indirection, less desirable.)

**Exit criteria**
- Selected option documented in `docs/modules/session_manager/README.md` with a short rationale.

---

## 5) Public schema surface (alias plan only)
[x ] Define the alias map to be exported by `schemas/__init__.py`:

- `SessionManagerStartInput  → {internal_start_input_class}`
- `SessionManagerStartOutput → {internal_start_output_class}`
- `SessionManagerEndInput    → {internal_end_input_class}`
- `SessionManagerEndOutput   → {internal_end_output_class}`

[ x] Verify names are unique across the project and fit the global `<Module>Input/Output` pattern.

**Exit criteria**
- Alias plan approved; no circular import risk (imports are one-way into module files).

---

## 6) Generator alignment (dry run)
[ x] Confirm `scripts/generate_schemas_from_master.py` resolves both session_manager_* modules from their **internal files** (not from `schemas/__init__.py`).
[ x] Update `scripts/schema_mapping_config.py` if needed so both modules produce:
- `*_schema.json`
- `*_input_example.json`
- `*_output_example.json`

**Exit criteria**
- Local dry run produces/updates JSON artifacts for start/end without errors.

---

## 7) Execute schema refactor (single, scoped change-set)
**In this order:**
1) In the **internal** schema files only, move `example_*()` to the correct class types (inputs have `example_input()`, outputs have `example_output()`), do not rename internal classes yet.
2) Add **explicit alias exports** to `schemas/__init__.py` per Step 5; update `__all__`.
3) Switch the unified router to import **only** from `schemas` (top-level public API).
4) Create `apps/session_manager/` façade (if using Option A) and wire the router to it. Keep old app folders intact for now.

**Exit criteria**
- `uvicorn` boots; `/session_manager/sessions.start` and `/session_manager/sessions.end` respond.
- `scripts/generate_schemas_from_master.py` still succeeds.
- Generated JSON examples reflect the corrected example method placement.

---

## 8) Add scoped guardrails (tests + CI)
[x ] Tests (scoped to session_manager for now):
- **Import policy:** fail if any route in `api/routes/` deep-imports `schemas.<submodule>`.
- **Public API presence:** assert that the four public aliases appear in `schemas.__all__`.

[x ] CI:
- Run tests in `.github/workflows/ci.yml`.
- Keep the guardrail scope limited to `session_manager` until ≥3 modules use the pattern.

**Exit criteria**
- CI green with guardrails enabled.

---

## 9) Decommission old structure (after green)
[ x] Remove `api/routes/session_manager_start_routes.py` and `session_manager_end_routes.py` once the unified router is active and tested.
[ x] Remove `apps/session_manager_start/` and `apps/session_manager_end/` once the new `apps/session_manager/` is active and referenced.
[ x] Update imports across the repo if any internal references to old app paths remain.

**Exit criteria**
- xGrep shows no references to the old route filenames or old app package paths.

---

## 10) Docs + changelog
[x ] `docs/CHANGELOG.md`: concise note of the refactor.
[x ] `docs/schemas/SCHEMA_CHANGELOG.md`: note example method corrections and public alias introduction.
[x ] `docs/getting started/CONTRIBUTING.md`: state “Routes import only from `schemas`” policy.

**Exit criteria**
- Documentation matches the shipped structure and names.

---

### All above are done. Jan 6, 2026

## Roll-forward Strategy
- Repeat Steps 0–10 module-by-module.
- After ≥3 modules migrated, widen guardrail search from module-scoped to project-wide.
- After all modules migrated, enforce policy globally and remove any temporary allowances.

---

## Risks / Mitigations
- **Generator drift:** Keep it pointed at internal files; do not couple to `schemas.__all__`.
- **Alias churn:** Lock public names now; any internal renames are invisible to routes.
- **Circular imports:** Only `schemas/__init__.py` imports internal modules; modules never import from `schemas`.
- **Route duplication:** Ensure only the unified `session_manager_routes.py` is included in `api/main.py`.
