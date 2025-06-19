# interfaces/ — External Schema Contracts

This directory contains JSON Schema definitions and example payloads for all data structures exchanged between A3CP modules and external components (e.g., frontend apps, collaborators, evaluators).

These are the public-facing, versioned **interface contracts** used for integration, testing, validation, and documentation.

## Purpose

- Provide an implementation-agnostic specification of valid message formats
- Ensure compatibility and testability across language, process, or network boundaries
- Define strict expectations for all payloads exchanged in the A3CP system

## Contents

- `*.schema.json`: JSON Schema definitions for each top-level message
- `examples/*.example.json`: Canonical example files for each schema

## Usage

- Each JSON Schema file corresponds to a Pydantic model in `schemas/`
- All schemas must include:
  - `$id`: A unique schema ID (e.g., "a3cp_message.schema.json")
  - `$schema`: Schema dialect version (e.g., "https://json-schema.org/draft/2020-12/schema")
  - `title`, `description`, `type`, and `properties`

- Each `.schema.json` file should link to:
  - Its example file (via `$comment` or docstring)
  - Its associated model in `schemas/`

## Validation Policy

- Every example file must pass validation against its corresponding schema
- Tests must enforce:
  - Example compliance
  - Schema validity via `jsonschema` or equivalent
  - Version consistency between `schemas/` and `interfaces/`

## Versioning

- Each schema must declare a `schema_version` field if used in the data payload
- Changes must follow semantic versioning ("MAJOR.MINOR")
- Backward-incompatible changes require a new MAJOR version and changelog entry

## Related Files

- `schemas/`: Python runtime models that correspond to these schemas
- `scripts/schema_diff.py`: Compares `.py` models to `.schema.json` definitions
- `docs/SCHEMA_REFERENCE.md`: Full human-readable schema reference

## Developer Notes

- These schemas must remain JSON Schema–compliant and self-contained
- Do not include runtime-only metadata (e.g., timestamps, session_id) unless relevant to contract
- Canonical source of truth for public message formats
