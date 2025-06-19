# schemas/ — Runtime Pydantic Models

This directory contains all runtime-validated pydantic models used internally by the A3CP system. These models define and enforce structured data formats exchanged between CARE modules during execution.

## Purpose

- Enforce strict runtime validation using pydantic (v2)
- Provide the canonical structure for all internal CARE messages
- Support versioned schemas with explicit upgrade paths
- Enable validation, testing, and message logging at runtime

## Usage Guidelines

- All files must define a top-level BaseModel from pydantic
- Each model must include a schema_version: str field
- Optional fields must have defaults (either explicit or None)
- Models must reference their matching interface schema via a constant:

  INTERFACE_SCHEMA_PATH = "interfaces/<filename>.schema.json"

- Every schemas/*.py model must be mirrored by:
  - A JSON Schema file in interfaces/*.schema.json
  - A JSON example in interfaces/examples/*.example.json

## Versioning Convention

- Use semantic versioning: "MAJOR.MINOR" (e.g., "1.0", "1.1")
- Any breaking change to a schema requires a bump in MAJOR
- Non-breaking additions or field default changes require a MINOR bump
- Schema evolution must be documented in SCHEMA_REFERENCE.md or the changelog

## Related Files

- interfaces/: Developer-facing JSON Schemas for external consumers
- interfaces/examples/: Canonical .json examples for each schema
- scripts/schema_diff.py: Tool to compare and audit schema changes

## Logging Requirements

- Any data rejected by these schemas must be logged to logs/provenance_log.jsonl
- Log entries should include:
  - timestamp
  - schema_name and schema_version
  - error_details
  - (optional) session_id or trace_id

## Developer Notes

- Do not import Django or FastAPI types into these models
- These models are designed for internal CARE system validation only
- FastAPI input/output models live separately under api/schemas/

## Example Schema Header

  from pydantic import BaseModel, Field

  INTERFACE_SCHEMA_PATH = "interfaces/a3cp_message.schema.json"

  class A3CPMessage(BaseModel):
      schema_version: str = Field(default="1.0", frozen=True)
      # ... more fields ...
