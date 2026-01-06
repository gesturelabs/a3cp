# Route Re-Migration Checklist (apply per module / per `api/routes/<module>_routes.py`)

## Goal
For each route file under `api/routes/`, ensure it imports schemas only from the public surface (`from schemas import ...`), while the generator continues to load schemas from internal files, and CI guardrails prevent regressions.

---

## A) Inventory (read-only)
1. Identify the route file(s):
   - `api/routes/<module>_routes.py` (and any legacy split files)
2. Identify which schema classes it currently imports.
3. Locate the internal schema file(s) that define those classes.

Exit: you can list `{internal_schema_file → classes used by route}`.

---

## B) Internal schema sanity (no behavior change)
4. In each internal schema file:
   - Confirm Input classes define `example_input()`.
   - Confirm Output classes define `example_output()`.
   - Do not rename classes unless required for correctness.
   - Keep validation rules intact.

Exit: internal schemas are coherent; examples live on the correct class type.

---

## C) Generator alignment (must load internal files, not public API)
5. Confirm `scripts/schema_mapping_config.py` points the generator at internal schema files for this module (file path/module path resolution).
6. Run generator for the module (or full run):
   - Verify it emits:
     - `<module>_schema.json`
     - `<module>_input_example.json`
     - `<module>_output_example.json`

Exit: generator succeeds and artifacts update without errors.

---

## D) Public schema surface (add/adjust exports)
7. Add/confirm exports in `schemas/__init__.py`:
   - Export the schema classes the route needs via stable public names.
   - Prefer `<Module>Input` / `<Module>Output` naming where feasible.
   - Ensure names are listed in `__all__`.

Exit: `python -c "from schemas import <PublicName>; print(<PublicName>)"` works for each exported symbol.

---

## E) Route rewrite (structure-only; no behavior redesign)
8. Update the route file to import schemas only from `schemas`:
   - Replace any deep imports:
     - `from schemas.<submodule> import ...`
     - `import schemas.<submodule>`
   - With:
     - `from schemas import ...`
9. Ensure the router is mounted once (no duplicate routers for the same module).

Exit: app boots; route paths appear once.

---

## F) HTTP smoke verification (minimal)
10. Boot and hit endpoints (stub OK):
   - `uvicorn api.main:app`
   - Confirm each endpoint responds (even 501 is acceptable if intended), but it must not crash on import/validation.

Exit: endpoint responds; no import errors; Swagger shows route once.

---

## G) Scoped guardrails (tests + CI)
11. Add a module-scoped test to enforce import policy for this module’s route file:
   - Fail if it deep-imports `schemas.<submodule>`.
12. Add/extend a public-API presence test:
   - Assert the module’s required public schema names are in `schemas.__all__`.

Exit: `pytest` passes locally and in CI.

---

## H) Decommission legacy (only after green)
13. Remove legacy split route files and/or old app packages once the unified route path is active and referenced.
14. Grep to confirm no remaining references to old filenames or old package paths.

Exit: repository has no references to legacy routes/apps for this module.

---

## Roll-forward rule
- Migrate modules in the demonstrator chain first.
- After ≥3 modules migrated, widen the import guardrail from module-scoped to repo-wide with a temporary allow-list.
- After all modules migrated, remove allow-list and enforce globally.
