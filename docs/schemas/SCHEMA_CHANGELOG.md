# SCHEMA_CHANGELOG.md

This changelog tracks all schema-related changes in the A3CP system, including structural updates to `schemas/*.py`, generated `interfaces/*.schema.json`, and example payload formats.

All entries follow [Semantic Versioning](https://semver.org/) and must align with the `schema_version` field embedded in runtime messages.

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
