# SCHEMA_EVOLUTION_POLICY.md

This document defines how schema changes are managed in the A3CP system to ensure stability, traceability, and compatibility across modules.

---

## 1. Semantic Versioning

All schemas must declare a `schema_version` field using [Semantic Versioning](https://semver.org/) format:

MAJOR.MINOR.PATCH


- **MAJOR**: Breaking changes (field removal, renaming, required status changes)
- **MINOR**: Additive, non-breaking changes (new optional fields, new enum values)
- **PATCH**: Fixes, clarifications, or documentation-only updates

---

## 2. Change Classifications

| Change Type                     | Version Impact   | Notes                                        |
|--------------------------------|------------------|----------------------------------------------|
| Add optional field             | MINOR            | Must not affect existing validators          |
| Add required field             | MAJOR            | Breaks backward compatibility                |
| Remove field                   | MAJOR            | Must follow formal deprecation notice        |
| Rename field                   | MAJOR            | Treat as remove + add                        |
| Change field type              | MAJOR            | May cause parsing failure                    |
| Add enum value                 | MINOR            | OK if consumers ignore unknown values        |
| Remove enum value              | MAJOR            | May break consumers with hardcoded values    |
| Modify schema metadata only    | PATCH            | Includes title, description, examples        |

---

## 3. Deprecation Policy

- Deprecated fields must remain valid for one MINOR version.
- Mark deprecations in `SCHEMA_REFERENCE.md` and `SCHEMA_CHANGELOG.md`.
- Removal must be scheduled for the next MAJOR release.

---

## 4. Changelog Format

All changes must be logged in `SCHEMA_CHANGELOG.md` with the format:

v1.1.0 - 2025-07-01
Added

    output_mode (AAC output format) to A3CPMessage

Changed

    Clarified context_prompt_type allowed values

Deprecated

    vector field (will be removed in v2.0.0)
