# SCHEMA_CHANGELOG.md

This changelog tracks all schema-related changes in the A3CP system, including structural updates to `schemas/*.py`, generated `interfaces/*.schema.json`, and example payload formats.

All entries follow [Semantic Versioning](https://semver.org/) and must align with the `schema_version` field embedded in runtime messages.

---


# SCHEMA_EVOLUTION_POLICY

All A3CP schemas must follow Semantic Versioning (MAJOR.MINOR.PATCH).

## Versioning Rules

| Change                          | Version Bump |
|---------------------------------|--------------|
| Add optional field              | MINOR        |
| Add required field              | MAJOR        |
| Remove or rename field          | MAJOR        |
| Change field type               | MAJOR        |
| Add enum value                  | MINOR        |
| Remove enum value               | MAJOR        |
| Metadata/documentation only     | PATCH        |

## Deprecation Policy

- Deprecated fields must remain parsable for ≥1 MINOR version.
- Removal requires explicit deprecation notice in `SCHEMA_CHANGELOG.md`.
- Deprecations must be marked in `.schema.md` and `SCHEMA_REFERENCE.md` (if applicable).

## Changelog Format (in SCHEMA_CHANGELOG.md)

Each change must include:

```text
v1.1.0 - 2025-07-01
Added:
  - output_mode (AAC output format) to A3CPMessage

Changed:
  - Clarified context_prompt_type allowed values

Deprecated:
  - vector field (removal planned in v2.0.0)



---

## ✅ Action Summary

| Action | Recommendation |
|--------|----------------|
| Keep file? | **Yes** (merge into `SCHEMA_CHANGELOG.md` or leave as reference in `/docs/`) |
| Rename? | Optional: `SCHEMA_VERSIONING_POLICY.md` (clearer intent) |
| Replace with automation? | Eventually yes — schema CI linter should enforce this |
| Duplicate content? | Avoid; ensure `.schema.md` files point to this for version rules |

---




## v1.0.0 – 2025-06-22

### Added
- Initial release of unified `A3CPMessage` schema (`schemas/a3cp_message.py`)
- Raw input schema: `raw_action_record.py`
- Clarification tracking: `clarification_event.py`
- Inference trace logging: `inference_trace.py`

### Structure
- Introduced `schema_version` field (required in all top-level schemas)
- Added sample input/output payloads to `docs/modules/*/`

---

(Each future release should follow this format.)

Let me know when you want to auto-generate or append to this file.
