# CHANGELOG.md


============================================================
 A3CP CHANGELOG — Infrastructure + Dev Flow
============================================================

Tag: v0.2.1-dev
Start Date: 2025-06-11
Maintainer: Dmitri Katz

### CHANGELOG - 2025-08-06

- Removed legacy pages app (all files and migrations deleted)
- Removed obsolete streamer app (all files deleted)
- Deleted ui app routing files (urls.py, views.py) for UI refactor
- Updated docs/FILE_TREE.txt and docs/architecture/a3cp_pipeline.drawio for new structure
- Added new app folders:
  - apps/ui/ (initial files and README)
  - apps/session_manager_start/ and apps/session_manager_end/ scaffolded
- Created archival folders for legacy code:
  - apps/old_pages/
  - apps/old_ui/


### CHANGELOG - 2025-08-06

[api/main.py]
- Updated to import and include separate routers for session start and end.
- Removed combined session_manager router.

[api/routes/session_manager_routes.py]
- Deleted combined session_manager routes file.

[schemas/session_manager/]
- Deleted combined session_manager schema files and examples.

[api/routes/session_manager_start_routes.py]
- Added route file for session start endpoint.

[api/routes/session_manager_end_routes.py]
- Added route file for session end endpoint.

[schemas/session_manager_start/]
- Added schema files for session start.

[schemas/session_manager_end/]
- Added schema files for session end.

### CHANGELOG - 2025-08-06

[docs/modules/session_manager/README.md]
- Revised session_manager documentation for clarity on lifecycle, inputs, outputs, and responsibilities.
- Expanded functional and non-functional requirements.
- Aligned document structure with project standards.

[schemas/base/base_schema.py]
- Updated for Pydantic v2 compatibility.
- Replaced deprecated enum validation with Literal.
- Refined field descriptions and optionality.

[schemas/session_manager/session_manager.py]
- Corrected example_output in SessionStartResponse:
  - Removed modality (unknown at session start).
  - Set source to "session_manager".
- Ensured SessionStartRequest and Response align with BaseSchema and schema design.


## [module_architecture] - 2025-08-01

### Updated
- Finalized MVP module selection (blue outline) based on system flow chart
- Marked core (internal) modules with **magenta star** and Docker modules with **Docker icon**
- Deferred post-MVP modules marked with **orange outline**

### MVP Modules (Blue Outline)
- ✅ Core (Magenta Star): `session_manager`, `input_broker`, `confidence_evaluator`, `memory_integrator`,
  `output_expander`, `output_planner`, `partner_ui`, `schema_recorder`
- 🐳 Dockerized: `audio_feed_worker`, `camera_feed_worker`, `speech_transcriber`, `landmark_extractor`,
  `gesture_classifier`, `sound_classifier`, `speech_context_classifier`, `visual_environment_classifier`,
  `model_trainer`, `sound_playback`, `landmark_visualizer`

### Post-MVP (Orange Outline)
- `llm_clarifier`, `feedback_log`, `retraining_scheduler`, `memory_interface`

### Storage Modules
- `model_registry` and `recorded_schemas` to remain internal on Hetzner, accessed via local endpoints



## [a3cp_core] - 2025-07-31

### Added
- Defined canonical `A3CPMessage` schema in `schemas/a3cp_core/a3cp_message.py` based on Section 2 of `SCHEMA_REFERENCE.md`
  - Includes required core metadata fields: `schema_version`, `record_id`, `user_id`, `session_id`, `timestamp`, `modality`, `source`
  - Supports forward-compatible extension via `extra = "allow"`
- Added schema validation utility in `schemas/utils/validate.py`
  - Function `validate_a3cp_message(data: dict)` raises on malformed messages
- Added unit test: `tests/schemas/test_a3cp_message.py`
  - Validates correct messages pass
  - Ensures missing or invalid fields are rejected


### CHANGELOG ENTRY - 2025-07-31


[Schema] Added Section 3.4: Classifier Output Components

- Introduced optional `classifier_output_components` field to support multimodal intent tracing.
- Allows downstream modules to inspect per-modality predictions (e.g., gesture, sound, speech).
- Each entry includes `intent`, `confidence`, and optional `timestamp`.
- Documented structure in Section 3.4 of the A3CPMessage specification.

Reason: Enables transparent, auditable contribution tracking when multiple classifiers inform a single semantic intent.


## [speech_context_classifier] - 2025-07-30

### Added
- Finalized `SpeechContextClassifierInput` model with partner speech and vocabulary fields
- Finalized `SpeechContextClassifierOutput` model aligned with A3CPMessage structure
- Defined nested `ClassifierOutput` and `ClassifierRankingItem` classes for result structure

### Generated
- `speech_context_classifier.schema.json` from validated Pydantic models
- `input.example.json` and `output.example.json` for documentation and test use


## [speech_context_classifier] - 2025-07-30

### Updated
- Removed undocumented `classifier_output.flags` field to align with SCHEMA_REFERENCE.md
- Deleted `relevance_scores` from Outputs section (not part of schema; replaced by `ranking`)
- Clarified that `classifier_output.intent` may be `null` and `ranking` empty when no match is found
- Explicitly listed `schema_version` and `record_id` as required fields in Outputs


## 2025-07-30  memory_integrator/README.md
- Rewrote module doc to align with updated schema and coordination flow
- Clarified that input comes from memory_interface and confidence_evaluator
- Specified that it outputs modifiers, not standalone A3CPMessages
- Added JSON output block with memory fields
- Added schema compliance summary

## [2025-07-30] Clarification of Routing and CARE Integration: confidence_evaluator

- Corrected downstream flow in `CARE Integration` section:
  - Now correctly routes through `clarification_planner` before reaching `output_expander`
- Clarified that the module mutates existing `A3CPMessage` records with updated scoring fields
- Confirmed compliance with `SCHEMA_REFERENCE.md` for `classifier_output`, `final_decision`, and `context.flags`


## [2025-07-30] Schema Pass-Through and Fusion Logic: input_broker

- Declared `input_broker` as a non-emitting, schema-pass-through module
  - Receives validated `A3CPMessage` inputs from gesture, sound, speech, and visual classifiers
  - Does not generate or mutate schema fields
  - Optionally annotates message groups with `stream_segment_id`

- Added Module Usage Matrix showing read-only access to all input fields
- Clarified CARE Integration role as first multimodal fusion point
- Documented internal output bundle format (not schema-validated, but traceable)

Maintains strict compliance with `SCHEMA_ARCHITECTURE.md` one-message-per-input rule.


## [2025-07-30] Schema & Model Update: visual_environment_classifier

- Declared `visual_environment_classifier` as schema-compliant (partial `A3CPMessage`)
  - Emits `context_location`, `context.flags`, and standard metadata fields
  - Sets `modality = "image"`, `source = "communicator"`
  - Output consumed by `input_broker` for context fusion

- Added Module Usage Matrix with downstream field mapping
- Included structured JSON output example with location and flags
- Clarified model design:
  - Uses a shared, static environment classifier (e.g., CNN)
  - Does not access or depend on `model_registry`


## [2025-07-30] Schema Alignment & CARE Integration Fixes

- `gesture_classifier`:
  - Declared compliant output via `classifier_output` in `A3CPMessage`
  - Added `ranking` field example for top-N predictions
  - Corrected CARE Integration section to reflect actual graph:
    - Receives input from `landmark_extractor`
    - Outputs only to `input_broker`
    - Removed incorrect links to `CARE Engine` or `clarification_planner`

- `sound_classifier`:
  - Revised CARE Integration section:
    - Clarified output to `input_broker` for fusion
    - Removed incorrect implication of direct CARE Engine interaction
    - Documented optional API exposure (`/api/sound/infer/`)


## [2025-07-30] Schema Compliance: speech_context_classifier

- Updated `speech_context_classifier` documentation to align with A3CP schema rules:
  - Declared production of partial `A3CPMessage` with `classifier_output`
  - Added support for `ranking` field: top-N intent-confidence pairs
  - Ensured `intent` and `confidence` fields are always present for compatibility
  - Included structured example with multiple ranked predictions
  - Added Module Usage Matrix showing downstream field consumption

Clarifies one-message-per-utterance design while supporting soft intent ranking.

## [2025-07-30] Schema Compliance Updates — A3CPMessage Integration

- Updated `speech_transcriber` module documentation:
  - Declared output of finalized transcript segments as `A3CPMessage`
  - Added schema compliance summary and example payload
  - Inserted Module Usage Matrix for compatibility with downstream classifiers

- Updated `landmark_extractor` module documentation:
  - Confirmed schema-compliant output via `raw_features_ref`
  - Declared required metadata fields (modality, source, vector_version, etc.)
  - Added Module Usage Matrix covering `gesture_classifier` and `schema_recorder`
  - Included example A3CPMessage with external vector reference



v0.5.5 - 2025-07-29

Changed
- Rewrote `audio_feed_worker/README.md` for consistency with SCHEMA_REFERENCE.md v1.1.
- Standardized runtime config description and output payload structure.

Removed
- Deprecated schema files moved to `docs/older version/`:
  - SCHEMA_REFERENCE.md (pre-v1.1)
  - SCHEMA_EVOLUTION_POLICY.md
  - SCHEMA_MAPPING.md
  - SCHEMA_OVERVIEW.md
  - old_video_streamer/README.md and notes.md

Fixed
- test_session_manager_routes.py: adjusted schema example path to match new schema naming c

## v1.1.0 – 2025-07-29

### Added
- Finalized and validated `audio_feed_worker.schema.md` with clarified output format, configuration source, and compliance disclaimer

### Changed
- `test_session_manager_routes.py`: updated to align with new schema linting expectations
- `docs/modules/session_manager/README.md`: updated integration notes to reflect schema routing logic

### Removed
- `SCHEMA_EVOLUTION_POLICY.md`: folded into top of `SCHEMA_CHANGELOG.md` and schema architecture
- `SCHEMA_MAPPING.md`: replaced by CI mapping test (`test_schema_mapping.py`)
- `SCHEMA_OVERVIEW.md`: deprecated flat view of A3CPMessage schema
- `docs/older version/SCHEMA_REFERENCE.md`: outdated copy removed
- `docs/older version/old_video_streamer/README.md`: removed legacy video/audio module notes
- `docs/older version/old_video_streamer/notes.md`: removed internal comments on defunct implementation


===============================
A3CP Changelog – 2025-07-28
===============================
### Added
- Scaffolded test for `/api/schema_recorder/` route
  - Loads input example from schema
  - Asserts 501 stub response
  - Placeholder for full output check post-implementation
### Added
- Scaffolded test for `/api/model_trainer/` route
  - Loads input example from schema
  - Asserts 501 stub response
  - Placeholder for full output check post-implementation

### Added
- Scaffolded test for `/api/output_planner/` route
  - Loads input example from schema
  - Asserts 501 stub response
  - Placeholder for full output check post-implementation

### Added
- Scaffolded test for `/api/output_expander/` route
  - Loads example input via `load_example()`
  - Asserts 501 stub response
  - Output comparison placeholder included for future implementation

### Added
- Scaffolded test for `/api/model_registry/` route
  - Loads input via `load_example()`
  - Asserts 501 stub response
  - Output assertion stub included for future implementation

### Added
- Scaffolded test for `/api/memory_interface/` route
  - Loads example input via `load_example()`
  - Asserts 501 stub response
  - Output comparison placeholder included for future implementation

## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/memory_integrator/` route
  - Loads example input via `load_example()`
  - Asserts 501 stub response
  - Output comparison placeholder included

## [0.5.x] - 2025-07-28

### Added
- Replaced hardcoded test for `/api/llm_clarifier/` with schema-based version
  - Uses `load_example()` for input consistency
  - Asserts 501 stub response
  - Output comparison placeholder included
## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/landmark_visualizer/` route
  - Loads example input via `load_example()`
  - Asserts 501 stub response
  - Output validation stub included for future implementation


## [0.5.x] - 2025-07-28

### Added
- Full test for `/api/landmark_extractor/` route
  - Uses `LandmarkExtractorInput.example_input()` and `tiny_jpeg_base64`
  - Verifies image decoding works
  - Asserts frame ID, user ID, and landmark structure in response

## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/input_broker/` route
  - Uses `load_example()` for structured input
  - Asserts 501 stub response
  - Output assertion stub included for future implementation


## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/gesture_classifier/` route
  - Uses example input via `load_example()`
  - Asserts 501 stub response
  - Output check block included for future implementation

## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/feedback_log/` route
  - Uses example input via `load_example()`
  - Expects 501 error response for now
  - Full output match block included, ready to enable

## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/confidence_evaluator/` route
  - Loads input via `load_example()`
  - Asserts 501 error response
  - Output validation stub included for future implementation


## [0.5.x] - 2025-07-28

### Added
- Scaffolded test for `/api/clarification_planner/` route
  - Uses `load_example()` for input
  - Asserts 501 error response
  - Output validation stub included, ready for future implementation


## [0.5.x] - 2025-07-28
### Added
- Scaffolded test for `/api/camera_feed_worker/` route
  - Uses `load_example()` for input/output
  - Asserts 501 response until implemented
  - Includes commented output assertions for future enablement

### Changed
- Refactored `test_audio_feed_worker_routes.py` to load input and output from JSON schema examples
- Replaced hardcoded test input with `load_example()` from `tests/utils.py`
- Added `assert_valid_iso8601()` utility to validate timestamp format in dynamic responses

## [0.5.x] - 2025-07-28

### Fixed
- Moved `example_input()` to correct class (`LandmarkVisualizerInput`) for test compatibility

### Added
- Test for `landmark_visualizer` stub route using example input and response schema


### Added
- Test for `landmark_extractor` route with full schema compliance and image decoding
- `tiny_jpeg_base64` fixture in `conftest.py` for use across image-processing module tests

### Changed
- Updated `landmark_extractor_routes.py` to decode base64 image input using Pillow
- Added Pillow to `requirements.txt`


[0.5.x] – Ongoing Development
-----------------------------
### Changed
- Refactored `scripts/generate_schemas_from_master.py` to support schema folders with multiple `.py` files (e.g. `__init__.py`)
- Regenerated all schema JSON files and input/output examples across existing modules


ADDED
-----
- Stub FastAPI routes created:
  - confidence_evaluator_routes.py
  - feedback_log_routes.py
  - gesture_classifier_routes.py
  - input_broker_routes.py
  - landmark_extractor_routes.py

- Each route includes:
  - POST / endpoint
  - Typed input/output models (placeholders)
  - Raises NotImplementedError (501)

- Started work on realistic I/O for landmark_extractor:
  - Identified expected input: frame or RGB image
  - Identified expected output: structured landmark vectors (x, y, z)

CHANGED
-------
- landmark_extractor_routes.py:
  - Removed circular placeholder model use
  - Planned schema model to reflect real MediaPipe-style output

- generate_schemas_from_master.py:
  - Script executes and finds all schema files
  - Does not produce output → silent failure suspected
  - Investigated issues in process_schema_module()

DEBUGGING NOTES
---------------
- Hypothesis: model classes not detected due to:
  - Missing subclassing from BaseModel
  - Missing example_input or example_output
- Inserted plan to add debug logs for:
  - Model class discovery
  - Attribute detection

NEXT STEPS
----------
- New thread: debug and fix schema generation script
- Finalize proper schema for:
  - landmark_extractor input: image or frame metadata
  - landmark_extractor output: normalized 3D landmarks


## [0.5.x] - 2025-07-25

### Added
- `AudioFeedWorkerConfig` POST test via `/api/audio_feed_worker/` with full request/response validation
- New test fixture `async_client` using `httpx.AsyncClient` and `ASGITransport`

### Changed
- `api/main.py`: verified and updated router imports and app mounting
- `tests/api/test_audio_feed_worker_routes.py`: converted to async + working integration test
- `tests/conftest.py`: added reusable `async_client` fixture for FastAPI tests
- `.github/workflows/ci.yml`: CI minor config changes
- `api/settings.py`: config tweak
- `pyrightconfig.json`: updated paths or type-checking scope
- `docs/FILE_TREE.txt`: updated structure to match refactored layout
- `docs/architecture/a3cp_pipeline.drawio`: added architecture diagram: user_profile to speech_context_module lost in disaster.

### Removed
- `docs/modules/inputs_outputs_json.md`: obsolete, replaced by `architecture/inputs_outputs_json.md`

### Notes
- CI now passes with fully working import paths (`PYTHONPATH=.` from `.env`)
- `requirements.txt` updated — consider running `pip freeze > required.txt` if locked dependencies are needed



## [Unreleased] - 2025-07-25

### Fixed
- Resolved Pylance `reportCallIssue` error on `from api.main import app` by adding `extraPaths: ["."]` to `pyrightconfig.json`.

### Added
- Added `__init__.py` files to all subdirectories in `schemas/` to ensure consistent package recognition by Python and static analyzers.

### Changed
- Updated `.github/workflows/ci.yml` to explicitly set `PYTHONPATH` using `${{ github.workspace }}` for reliable module resolution during CI runs.
- Modified `docs/FILE_TREE.txt` to reflect addition of `__init__.py` files and confirm schema structure compliance.
- Edited `tests/api/test_audio_feed_worker_routes.py` to ensure import of `app` from `api.main` functions correctly in both runtime and static analysis environments.

====================================================================
CHANGELOG ENTRY – 2025-07-25
Category: Recreating Documentation, Schema, Module Integration after serious error
====================================================================

### Added
- Created route stubs for all 24 core A3CP modules:
  - `audio_feed_worker`, `camera_feed_worker`, `clarification_planner`, `confidence_evaluator`
  - `feedback_log`, `gesture_classifier`, `input_broker`, `landmark_extractor`
  - `landmark_visualizer`, `llm_clarifier`, `memory_integrator`, `memory_interface`
  - `model_registry`, `model_trainer`, `output_expander`, `output_planner`
  - `retraining_scheduler`, `schema_recorder`, `session_manager`
  - `sound_classifier`, `sound_playback`, `speech_context_classifier`, `speech_transcriber`
  - `visual_environment_classifier`

- All routes are registered in `api/main.py` under `/api/<module_name>/`

### Removed
- Deprecated monolithic route handlers:
  - `gesture_infer.py`, `sound_infer.py`, `streamer.py`, `inference.py`, and corresponding tests

### Changed
- Updated `docs/modules/inputs_outputs_json.md` and `a3cp_pipeline.drawio` to reflect modular architecture
- Finalized schema placement and naming for `speech_context_classifier`

### Notes
- Module route stubs currently raise `501 Not Implemented`; test coverage to follow
- Schema → Route → Test development workflow documented in `docs/dev/Schema → Route → Test Workflow.md`



Removed:
- Deprecated legacy schemas under `api/schemas/` after full migration to module-based schema structure.




====================================================================
CHANGELOG ENTRY – 2025-07-21
Category: Documentation, Schema, Module Integration
====================================================================

Added:
------
- docs/modules/partner_ui/README.md
  - Defined responsibilities, inputs, and outputs for partner-facing UI module
  - Documents clarification prompt rendering, feedback routing, and session note handling

- docs/modules/recorded_schemas/README.md
  - Describes the persistent schema archive module
  - Details append-only message storage, retrieval by session/user/modality, and integration with retraining, visualization, and playback modules

- docs/modules/user_profile_store/README.md
  - Defines the role of user-specific configuration and vocabulary memory
  - Describes how preferences and mappings inform CARE Engine, clarification planner, and output planner

- schemas/speech_context_classifier/speech_context_classifier.py
  - Pydantic schema for input/output of `speech_context_classifier`
  - Includes structured fields for prompt type, matched intents, relevance scores, context flags, and session/user metadata

====================================================================
Impact:
--------
- Introduces key documentation for partner-facing and memory-backed modules
- Finalizes schema stub for speech context inference
- Enables upcoming CARE integration and structured logging for partner feedback and training memory

Version: v0.4.3-dev
Author: core-dev

====================================================================
CHANGELOG ENTRY - 2025-07-21
Category: Schema, Module Docs, Clarification Logic
====================================================================

Modified:
---------
- docs/architecture/a3cp_pipeline.drawio
  - Updated module flow to reflect `clarification_planner` outputs to `feedback_log` and `memory_interface`
  - Corrected data flow arrows for context flags and memory metadata

- docs/modules/clarification_planner/README.md
  - Overhauled responsibilities to match schema and module manifest
  - Added structured output fields: `clarification`, `final_decision`, and `decision_metadata`
  - Removed reference to non-existent `audit_log`

- docs/modules/inputs_outputs_json.md
  - Refined `outputs_to` for multiple coordinator modules to reflect clarification updates
  - Ensured consistency with `module_name` and `module_type` taxonomy

- docs/schemas/SCHEMA_REFERENCE.md
  - Updated Section 6.4: `clarification.*` object fields and downstream usage
  - Added guidance on forwarding `decision_metadata` to `feedback_log` and `memory_interface`
  - Removed legacy reference to `audit_log` as an output sink

- schemas/clarification_planner/clarification_planner.py
  - Refactored output model to match A3CP schema: uses `clarification`, `final_decision`, `decision_metadata`
  - Deprecated ambiguous field `clarification_trigger`
  - Introduced `ClarificationMetadata` object and removed legacy `clarification_payload`

====================================================================
Impact:
--------
- Schema and planner output now fully aligned with `SCHEMA_REFERENCE.md`
- Clarification planner integrates cleanly into memory and feedback workflows
- Removed outdated `audit_log` terminology across code and documentation

Version: `v1.0.0-schema-sync`
Author: core-dev
====================================================================


============================================================
CHANGELOG ENTRY - 2025-07-21
Category: Architecture, Validation, Schema Wiring
============================================================

✔ Verified and validated updated module I/O definitions
   - Confirmed consistency of 30+ modules in the A3CP pipeline
   - Checked symmetry of `inputs_from` and `outputs_to` across all modules
   - Evaluated for acyclic structure, logical modularization, and integration coherence
   -added module_type to input_outputs_json.md

✘ Identified and resolved:
   - [Syntax] Trailing comma in `partner_ui.inputs_from` → removed
   - [Missing Definition] `user` listed as source for `session_manager` but not defined
     → recommendation: define as external system boundary or dummy module

🧠 Observations:
   - Modular design cleanly separates sensory input, model inference, memory, clarification, and output
   - All dataflow paths between classifiers, broker, planner, and UI layers are traceable and logically valid


====================================================================
CHANGELOG ENTRY - 2025-07-21 - Schema I/O Validation
Category: Validation, Schemas, Developer Tooling
====================================================================

Fixes & Improvements:
---------------------
- Performed structural validation of module-level input/output links across A3CP schema.
- Identified 9 modules with missing `outputs_to` links from expected upstream producers.
- Identified 4 modules with `outputs_to` declarations that are not matched by any declared consumer.
- Corrected previous typo: replaced `"recorded_schema"` with `"recorded_schemas"` in all affected modules.
- Verified module count and interconnection completeness (25 modules total).
- Confirmed cycles and loopbacks (e.g., `feedback_log -> memory_interface -> ...`) are valid in runtime DAG context.
- Highlighted undefined external systems: `user_input_pipeline`, `config_man


### Infrastructure
- Added new module: `retraining_scheduler` for policy-based model retraining
- Created `schemas/retraining_scheduler/` with Pydantic models for:
  - `RetrainingRequest`
  - `RetrainingDecisionLog`
- Added `docs/modules/retraining_scheduler/README.md` with responsibilities, inputs/outputs, and trigger logic

### Architecture
- Updated `a3cp_pipeline.drawio` to reflect new `retraining_scheduler` module and directional conventions (input: top, output: bottom)

### Documentation
- Updated `inputs_outputs_json.md` to include `retraining_scheduler` in system schema map


## [v0.5.x] - 2025-07-17

### Architecture
- Updated `docs/architecture/a3cp_pipeline.drawio` to reflect revised module I/O structure
- Updated `docs/FILE_TREE.txt` to match current file and module layout

### Module Documentation
- Renamed `speech_context_inferer/README.md` to `speech_context_classifier/README.md`
- Added new module doc: `user_profile_store/README.md`
- Added `inputs_outputs_json.md` for centralized JSON representation of module I/O

### Schema Changes
- Updated schemas and examples:
  - `audio_feed_worker`
  - `camera_feed_worker`
  - `clarification_planner`
  - `confidence_evaluator`
  - `feedback_log`
  - `gesture_classifier`
  - `input_broker`
  - `landmark_extractor`
  - `schema_recorder`

- Added schemas and examples:
  - `landmark_visualizer`
  - `llm_clarifier`
  - `memory_integrator`
  - `memory_interface`
  - `model_registry`
  - `model_trainer`
  - `output_expander`
  - `output_planner`
  - `session_manager`
  - `sound_classifier`
  - `sound_playback`
  - `speech_context_classifier`
  - `speech_transcriber`
  - `visual_environment_classifier`

### Timestamp
2025-07-17 18:14 CEST


## [v0.5.x] - 2025-07-14
### Schemas
- Added `schemas/visual_environment_classifier/visual_environment_classifier.py` with `VisualEnvironmentPrediction` model
- Defines structured scene classification output with environment label, confidence, and audit metadata
- Includes example input/output for logging and downstream consumption

### Schemas
- Added `schemas/speech_transcriber/speech_transcriber.py` with `SpeechTranscriptSegment` model
- Captures finalized or partial ASR output with timestamps, confidence, and session linkage
- Supports transcript logging and streaming into context modules
### Schemas
- Updated `schemas/speech_context_inferer/speech_context_inferer.py` to define `SpeechContextInfererInput` and `SpeechContextInfererOutput`
- Includes `PartnerSpeechSegment` and `VocabularyItem` submodels
- Preserves full structured context, relevance scoring, flags, and clarification triggers
- Conforms to A3CP schema style with `example_input()` and `example_output()` methods

### Schemas
- Added `schemas/sound_playback/sound_playback.py` with `AudioPlaybackRequest` model
- Defines structured metadata for reviewing previously recorded audio with playback controls
- Includes consent status, label context, and file path for traceable review
- Supports `example_input()` and `example_output()` for doc generation

### Schemas
- Added `schemas/sound_classifier/sound_classifier.py` with `SoundClassifierInput` and `SoundClassifierOutput` models
- Includes encoded audio input metadata and ranked intent prediction results
- Supports inference trace logging via structured schema with `example_input()` and `example_output()`

### Added
- Added `schemas/session_manager/session_manager.py` with `SessionStartEvent` and `SessionEndEvent` models
- Captures lifecycle of A3CP interaction sessions with user ID, timestamps, and optional context
- Includes `example_input()` and `example_output()` for each model to support doc generation

### Added
- Added `schemas/schema_recorder/schema_recorder.py` with `RecorderConfig` model
- Defines config options for structured logging (format, directory, hashing, rotation)
- Includes example input/output for automated `.json` schema generation

### Added
- Added `schemas/output_planner/output_planner.py` with `OutputPlannerInput` and `OutputPlannerDecision` models
- Includes `context` and `user_profile` echo fields for traceability
- Aligned with `output_expander.py` and full `SCHEMA_REFERENCE.md` v1.0.0 structure
- Added `example_input()` and `example_output()` for automated `.json` generation

### Added
- Added `output_expander.py` schema module:
  - `OutputExpansionInput` with support for context and user tone/style
  - `OutputExpansionResult` with `output_phrase`, `output_mode`, and audit metadata


## [v0.5.5] - 2025-07-14

### Added
- Introduced `model_trainer.py` schema module:
  - `TrainingRequest`: defines input structure for per-user model training jobs
  - `TrainingLogEntry`: defines structured output log with `status`, `metrics`, `artifact paths`, and `error_trace`
  - Enforces controlled vocabulary for training `status` (`"success"`, `"failure"`, `"partial"`)
  - Aligned field names with `model_registry` (e.g., `model_artifact_path`, `label_encoder_path`)
  - Includes `example_input()` and `example_output()` for schema generator integration


## [v0.5.5] - 2025-07-14

### Added
- Introduced `model_registry.py` schema module:
  - Defines `ModelRegistryEntry` for logging per-user model training events
  - Includes metadata fields: `user_id`, `modality`, `vector_version`, `timestamp`, `config`, `model_artifact_path`, `schema_version`, and optional `model_version`
  - Uses flexible `config: Dict[str, Any]` to support diverse training configurations
  - Includes `example_input()` and `example_output()` for registry entry generation

## [v0.5.5] - 2025-07-14

### Added
- Introduced `memory_interface.py` schema module:
  - `MemoryAuditEntry`: logs per-user memory interactions (`intent_label`, `label_status`, `final_decision`, etc.)
  - `MemoryQueryResult`: structured output with `intent_boosts`, `fallback_suggestions`, and `hint_used`
  - Nested `MemoryFields` model ensures compliance with `SCHEMA_REFERENCE.md` section 7 (memory-based output)
  - Includes `example_input()` for audit logs and `example_output()` for inference hinting




## [v0.5.4] - 2025-07-11

### Added
- Introduced `memory_integrator.py` schema:
  - Defines `MemoryIntegratorInput` with classifier outputs, memory intent boosts, and hint flags.
  - Defines `MemoryIntegratorOutput` with adjusted intent scores, optional final decision, and a logging summary.
  - Supports recency-, frequency-, and correction-based score adjustments using per-user memory traces.


## [v0.5.4] - 2025-07-11

### Added
- Introduced `llm_clarifier.py` schema:
  - Defines `LLMClarifierInput` with session metadata, intent candidates, topic tags, and CARE flags.
  - Defines `LLMClarifierOutput` with generated prompt string, prompt mode, updated flags, and logging summary.
  - Supports clarification prompt generation using local quantized LLMs.

## [v0.5.4] - 2025-07-11

### Added
- Introduced `landmark_visualizer.py` schema:
  - Defines `LandmarkVisualizerInput` and `LandmarkVisualizerOutput` models.
  - Supports rendering of landmark sequences from `.parquet` files.
  - Includes options for render mode (`animation`, `static`, `preview`) and export format (`gif`, `mp4`, `png`).
  - Designed for use in Streamlit UI and export pipelines.


## [v0.5.4] - 2025-07-11

### Changed
- Revised `landmark_extractor.py` schema to more accurately reflect MediaPipe Holistic output:
  - Clarified multi-stage inference process in module docstring.
  - Updated `z` description to note variable depth scale across body parts.
  - Noted that `visibility` is only defined for pose and hand landmarks.
  - Improved field-level descriptions for pose, hand, and face landmark sets.
  - Expanded `example_input()` to include representative landmarks from all four regions:
    pose, left hand, right hand, and face.
  - Confirmed that `example_output()` mirrors `example_input()` as expected for single-output modules.

### Notes
- This schema models the structured output of a single RGB frame from the holistic landmark pipeline.
- All fields in the example conform to the normalized coordinate system used by MediaPipe.


## [v0.5.3] - 2025-07-11

### Added
- Implemented schema modules with structured examples and unified naming:
  - `audio_feed_worker.py`: includes config model with `chunk_size`, `device_index`, and `sample_rate`.
  - `camera_feed_worker.py`: defines config with `device_id`, `resolution`, `frame_rate`, `camera_type`.
  - `clarification_planner.py`: defines `ClarificationPlannerInput` and output model for intent selection logic.
  - `feedback_log.py`: `FeedbackLogEntry` schema for caregiver feedback with optional label correction.
  - `gesture_classifier.py`: structured output of gesture inference results, including confidence distribution.
  - `input_broker.py`: multimodal `AlignedMessageBundle` for temporally aligned gesture/audio/speech inputs.
  - `landmark_extractor.py`: `HolisticLandmarkBundle` containing pose, face, and hand landmarks with normalized 3D coordinates.

### Changed
- Updated `generate_schemas_from_master.py` to:
  - Generate `*_schema.json` for **all** `BaseModel` classes in each module.
  - Extract examples (`*_input_example.json`, `*_output_example.json`) from the **first** class defining `example_input()` or `example_output()` methods.
  - Enforce single `.py` per schema folder and single example-defining class to prevent ambiguity.
  - Introduce static method convention for `example_input` and `example_output` to streamline inspection.

### Notes
- All schema modules are compliant with the canonical structure defined in `SCHEMA_REFERENCE.md`.
- Z-coordinates from MediaPipe are retained for future processing despite current 2D-only use in downstream logic.
- All generated examples are valid JSON and reflect realistic runtime payloads for each module’s role in the A3CP pipeline.


## [v0.5.2] - 2025-07-11
### Changed
- Updated `generate_schemas_from_master.py` to support structured example generation:
  - Generates `*_schema.json` from **all** `BaseModel` classes in the target `.py` file.
  - Generates `*_input_example.json` and `*_output_example.json` from **only the first** class in the file that defines `example_input()` or `example_output()` methods.
  - Prevents multiple example files from being generated per module.

### Requirements for Schema Modules
- Each schema folder (e.g. `schemas/audio_feed_worker/`) must contain exactly one `.py` file.
- That file may define multiple `BaseModel` classes, but:
  - Only one class should define `@staticmethod def example_input()` and/or `example_output()`.
  - All other classes must **not** define example methods to avoid ambiguity.

### Example Output
For a module named `foo_bar`, the script will produce:
- `schemas/foo_bar/foo_bar_schema.json`
- `schemas/foo_bar/foo_bar_input_example.json` (if `example_input()` exists)
- `schemas/foo_bar/foo_bar_output_example.json` (if `example_output()` exists)

## [v0.5.0] - 2025-07-10
### Added
- New script `generate_schemas_from_master.py` in `scripts/` for automatic schema and example file generation.
  - Iterates over all subdirectories of `schemas/`
  - For each directory containing a single `.py` file with a `BaseModel` subclass:
    - Generates `<module>_schema.json` using `model_json_schema()`
    - Calls `example_input()` and `example_output()` static methods (if present) to generate:
      - `<module>_input_example.json`
      - `<module>_output_example.json`
  - Supports `--module <name>` to restrict processing to a specific schema folder
  - Designed for consistent, reproducible generation of Pydantic-based schemas and examples


## [gesture_classifier] Schema Simplification & Boundary Correction – 2025-07-09

- Removed `audit_log` field from `GestureClassifierOutput` model and schema.
- Confirmed that `gesture_classifier` performs only ML inference and should not attempt context-aware explanation.
- Updated `output.example.json` to reflect minimal, valid structure (label → confidence).
- Cleaned Pydantic model and schema definitions to reinforce strict separation between classifier and downstream evaluators.

-----------
## [2025-07-09] Schema Feedback Log
[schemas] Added new module: feedback_log
 - Defined FeedbackLogEntry Pydantic model with audit-safe fields
 - Enforced enum-based label_status ("confirmed", "corrected", "rejected")
 - Generated feedback_log.schema.json
 - Added input.example.json and output.example.json with canonical test case
 - Aligns with CARE feedback loop and audit export specs
==============================

## [2025-07-09] Schema Updates – Clarification & Confidence Modules

- Refactored `clarification_planner.schema.json`:
  - Removed legacy structure
  - Added `$defs` for input/output schema separation
  - Added compliant `input.example.json` and `output.example.json`

- Added `confidence_evaluator.schema.json`:
  - Defined `RankedIntent`, `ConfidenceEvaluatorInput`, `ConfidenceEvaluatorOutput`
  - Supports weighted scoring, memory integration, and audit trail
  - Added schema-compliant examples for input and output

All schemas updated to use domain: https://gesturelabs.org

## 2025-07-09  clarification_planner
- Added ClarificationPlannerInput and ClarificationPlannerOutput schemas
- Generated clarification_planner.schema.json and example input/output JSON
- Supports audit-traceable clarification trigger decisions
- Conforms to SCHEMA_REFERENCE.md structure and CARE loop contract

## [2025-07-09] camera_feed_worker models and schema added

- ✨ Added camera_feed_worker.py with config and frame metadata models
- ✅ Schema aligned with A3CP SCHEMA_REFERENCE.md (modality=image, source=communicator)
- 🧪 Added input.example.json and output.example.json for validation
- 📄 Generated camera_feed_worker.schema.json
- 🔒 No raw frames are serialized; landmarks only are extracted downstream

## [2025-07-09] audio_feed_worker module added

- ✨ Added audio_feed_worker.schema.json (Config + Metadata models)
- ✅ Removed pseudonym field for strict A3CP compliance
- 📦 Added input.example.json and output.example.json
- 📝 Updated README to clarify role boundaries and schema alignment



## [v0.4.X] - 2025-06-25
### Added
- Implemented `speech_context_inferer.py` schema under `schemas/`
  - Defines input/output structures for contextual inference of partner speech
  - Handles transcript segments, partner dialog history, and user vocabulary mappings
- Generated JSON Schema: `schemas_json/speech_context_inferer.schema.json`
- Added validation examples:
  - `examples/speech_context_inferer/input.example.json`
  - `examples/speech_context_inferer/output.example.json`


## ✨ Added: Schema Generation for `gesture_classifier` Module

We completed the full schema and artifact generation process for the `gesture_classifier` module, establishing the standard pattern for all modules in A3CP. This includes:

### Files Generated
- `schemas/gesture_classifier.py`: Pydantic source file defining the `GestureClassifierInput` and `GestureClassifierOutput` models, along with reusable submodels (`FileReference`, `RawFeaturesRef`).
- `gesture_classifier/gesture_classifier.schema.json`: JSON Schema file containing both input and output message formats using `oneOf`, generated from the Pydantic models.
- `gesture_classifier/input.example.json`: Sample input message showing a realistic payload with feature vector reference and model/encoder artifacts.
- `gesture_classifier/output.example.json`: Sample output message showing classification predictions and referenced artifacts.

### Process Summary
1. **Model Authoring**
   Defined structured Pydantic models using `Annotated` and `Field(..., description=...)` for precise field metadata.

2. **Schema Generation**
   Used `model_json_schema()` from Pydantic to generate schemas. Combined input/output models manually using a `oneOf` union. Avoided unsupported JSON Schema features like `$dynamicRef`.

3. **Example Generation**
   Created realistic JSON instances for both input and output messages, referencing `.h5`, `.pkl`, and `.parquet` files with synthetic hashes.

4. **Folder Convention**
   All generated artifacts are stored under a flat `gesture_classifier/` directory:

## [2025-06-25] Module Documentation Refactor

### Added
- `README.md` files for new modules:
  - `audio_feed_worker`
  - `camera_feed_worker`
  - `schema_recorder`
  - `speech_context_inferer`
  - `landmark_extractor`
  - `visual_environment_classifier`

### Modified
- Finalized `README.md` files for all previously drafted modules:
  - `clarification_planner`, `confidence_evaluator`, `feedback_log`, `gesture_classifier`, `input_broker`,
    `landmark_visualizer`, `llm_clarifier`, `memory_integrator`, `memory_interface`, `model_registry`,
    `model_trainer`, `output_expander`, `output_planner`, `session_manager`, `sound_classifier`,
    `sound_playback`, `speech_transcriber`

### Removed
- All `notes.md` files from module directories
- Legacy `video_streamer` module and subcomponents:
  - `CameraFeedWorker.md`, `RecordingPipeline.md`, `README.md`, diagrams, and notes

## [Unreleased] - Schema Refactor & Canonical Mapping-2025-06-24
Docs Cleanup:
- Removed legacy example files from docs/modules/*
- Canonical example files now reside in schemas/examples/<schema_name>/


### Added
- `scripts/schema_mapping_config.py`: Centralized config defining canonical mappings between source schemas, JSON Schema files, and input/output examples.
- `schemas/source/`, `schemas/schema_json/`, `schemas/schema_examples/`: New directory structure for schema maintainability.
- `scripts/gen_schema_mapping.py`: Validates mapping and generates `SCHEMA_MAPPING.md`.

### Changed
- Refactored schema storage from `docs/modules/<module>/schema.json` to dedicated schema folders.
- Updated `SCHEMA_MAPPING.md` format to include source, schema, and input/output examples.

### Removed
- Deleted 20+ obsolete schema.json files from `docs/modules/`.

### Notes
- `SCHEMA_MAPPING.md` is now autogenerated and enforced.
- All schema components must pass validation during CI.


## [Unreleased] – 2025-06-23

### Removed
- Deleted all `schema.json` files from `docs/modules/*/` to eliminate redundant and outdated local schema definitions.
- These modules now reference centralized schemas in `schemas/` and exported JSON Schemas in `interfaces/`.

### Added
- `scripts/schema_mapping_config.py`: Defines the canonical mapping from schema definitions to interfaces and example files.
- `docs/schemas/`: New subdirectory for schema-related documentation and version tracking (e.g. SCHEMA_MAPPING.md, SCHEMA_CHANGELOG.md).

### Changed
- Reorganized `docs/` folder structure to separate schema documentation from module-specific notes and inputs.



### Added
- New schema: `schemas/clarification_event.py` for tracking disambiguation events in the CARE loop
- Corresponding test: `tests/schemas/test_clarification_event.py`
- Supports `clarification_type`, `trigger_reason`, options, response, and resolution metadata

### Added
- Added `schemas/inference_trace.py` schema for logging predictions, confidence, fallbacks, and decisions
- Added test file `tests/schemas/test_inference_trace.py` for validation of `InferenceTrace`
### Added
- Initial schema definition `schemas/raw_action_record.py` for A3CP input records using Pydantic v2 with strict validation (`extra="forbid"`), field annotations, and frozen versioning.
- Unit test suite `tests/schemas/test_raw_action_record.py` covering:
  - Valid instantiation
  - Missing required fields
  - Rejection of unexpected fields
- `.vscode/settings.json` to enforce formatting on save and auto-linting.
- `pyproject.toml` configuration with Black, Ruff, and isort alignment.
- `pyrightconfig.json` with `"basic"` type checking and import validation.

### Fixed
- Rewrote test assertions to comply with Pydantic v2 error messages (`extra_forbidden`, `ValidationError`).
- Ensured timezone-aware timestamps in all datetime fields for schema consistency.

## [Unreleased] – 2025-06-20
## [2025-06-20] Refactor and Modularize Video Streamer


### Changed
- Removed legacy `streamer` module:
  - `README.md`, `notes.md`, `sample_input.json`, `sample_output.json`, and `schema.json` deleted.

### Added
- New `video_streamer` module structure:
  - `CameraFeedWorker.md`, `LandmarkExtractor.md`, `RecordingPipeline.md` specifications.
  - `README.md` and `notes.md` for developer documentation.
  - `schema.json`, `sample_input.json`, and `sample_output.json` for input/output modeling.
  - `video_streamer_architecture.drawio` added under `diagrams/`.

### Modified
- `SCHEMA_REFERENCE.md` updated to reflect schema separation for `video_streamer`.




## [1.0.1] - 2025-06-19

### Added
- **Section 11: Module Usage Matrix** to schema documentation.
  - Maps field usage (read/write/update) across Streamer, Inference, Trainer, CARE Engine, and Feedback Logger modules.
  - Clarifies interface responsibilities and prevents schema drift.
  - Includes notes on composite fields (`context.*`) and forward compatibility.

### Notes
- No changes to field definitions; version remains backward-compatible (`MINOR` update).
- Update intended to support development planning and QA traceability.

## [Unreleased] – 2025-06-18
### Documentation

- Standardized `CONTRIBUTING.md` to align with `DEV_SETUP.md`
- Clarified structure, branch naming, and setup guidance


- Moved `SETUP.md` to `docs/DEV_SETUP.md` to align with development checklist structure.
- No content changes made; this remains the canonical developer onboarding guide.
### Added
- `DEVELOPMENT_FLOW.md`: Documents team Git workflow, branch protection rules, and deployment notes.


### Changed

- CI Pipeline: Updated `.github/workflows/ci.yml` to install both `requirements.txt` and `requirements-dev.txt`, ensuring development tools (e.g., `pytest`, `pre-commit`, `ruff`) are available during CI checks.
- Dev Requirements: Added `requirements-dev.txt` to isolate development-only dependencies from production installs.


### Added
- Environment validation script `scripts/check_env.py` with required/optional variable checks.
- `Makefile` target `check-env` to invoke the validation script easily.
- CI integration: added `check_env.py` check to GitHub Actions workflow to enforce env consistency.
- `.pre-commit-config.yaml` with hooks for black, ruff, isort, and EOF fixer
- `.github/workflows/lint.yml` GitHub Actions workflow for linting
- `pre-commit` added to `requirements-dev.txt`

### Changed
- Applied formatting, lint fixes, and import sorting across codebase
- `.env.example` updated to remove duplicate keys and clarify intended usage.

### Fixed
- Resolved `ModuleNotFoundError` for `fastapi` and `pydantic_settings` by updating virtual environment dependencies.
- Installed `pydantic-settings>=2.0,<3.0` to support Pydantic v2 settings API.
- Verified `fastapi`, `uvicorn`, and all schema dependencies are installed and test-compatible.
- All tests (`test_main_smoke.py`, `test_gesture_infer.py`, etc.) now pass cleanly in `.venv`.

### DevOps
- Ensured `.venv` is active and isolated from Anaconda conflicts.
- Added `pydantic-settings` to `requirements-dev.txt` for consistency.


## [2025-06-16] CI/CD: Restore Reliable GitHub → Hetzner Deployment

**Fixed:** Production server at Hetzner (`/opt/a3cp-app`) was out of sync with GitHub `main` despite functioning CI pipeline. Manual edits to server config had diverged the Git history, causing `git pull` to silently fail during deploy.

**Changes:**

- Ran `git fetch && git reset --hard origin/main` on Hetzner to force realignment with GitHub.
- Verified missing files (`api/routes/sound_infer.py`) now present.
- Reinstalled Python requirements and ran `migrate` to ensure app consistency.
- Restarted `gunicorn` to apply changes.

**Improvements:**

- `.env.example`: Added missing deployment port variables:
  - `GUNICORN_PORT=8000`
  - `UVICORN_PORT=8001`
- `.github/workflows/deploy.yml`: Verified correct steps for:
  - `git pull origin main`
  - Dependency install
  - DB migration
  - Static collection
  - Gunicorn restart

**SSH Key Fix:**

- Git push requested SSH passphrase unexpectedly.
- Diagnosed via `ssh-add -l` showing “The agent has no identities.”
- Fixed by running `ssh-add --apple-use-keychain ~/.ssh/github_a3cp_dev_ed25519`.
- Updated `~/.ssh/config` with:
  ```ssh
  AddKeysToAgent yes
  UseKeychain yes


## [0.2.2-dev] - 2025-06-16
### Added
- `scripts/manage.sh` script to centralize common dev tasks (e.g., `dev-api`, `dev-django`, `test`, `lint`, `format`)
- FastAPI `/openapi.json` smoke test in `test_main_smoke.py` to validate app import and route readiness
- Nginx configuration example for routing all `/api/` traffic to FastAPI (port 9000) in `docs/DEPLOYMENT.md`

### Deferred
- Latency test for `/api/feedback/` moved to backlog, pending endpoint implementation and route exposure

### Notes
- `scripts/manage.sh` reads `.env` automatically to support port configuration (`UVICORN_PORT`, `GUNICORN_PORT`)
- Smoke test uses `ASGITransport` and validates `/openapi.json` returns 200 with expected structure
- Nginx `/api/` block now replaces narrower `/api/infer/` example for broader route coverage

## [0.1.1] - 2025-06-12
### Added
- `/api/sound/infer/` endpoint for sound-based intent classification
- `api/schemas/sound_infer.py` defining A3CPMessage schema for modality='sound'
- Test coverage in `tests/api/test_sound_infer.py` using `@pytest.mark.anyio`
- Mounted `sound_infer.router` in `api.main`

### Notes
- Current implementation returns a placeholder response
- Follows same structure as `gesture_infer` for consistency



## [Feature] Add `/api/gesture/infer/` stub endpoint returning dummy A3CPMessage

- ID: API002
- Date: 2025-06-12
- Scope: api.routes.gesture_infer, api.main, tests/api

### Summary
Stub endpoint `/api/gesture/infer/` returns a dummy A3CPMessage-compatible JSON response.
Prepares groundwork for integrating the gesture classification model.

### Changes
- Added `gesture_infer.py` route handler with `@router.post("/gesture/infer/")`
- Mounted in `api.main` via `app.include_router(gesture_infer.router, prefix="/api")`
- Wrote test module `test_gesture_infer.py` covering:
  - HTTP 200 status response
  - Expected A3CPMessage fields present in response
  - Confidence scores in classifier_output are between 0.0 and 1.0
- Set `pythonpath = .` in `pytest.ini` to simplify local test execution

### Notes
- No real model inference yet — response is hardcoded
- Next step: load user-specific model and return real predictions

## [Fix] Pydantic v2 compliance and test import resolution

- ID: DEV002
- Date: 2025-06-12
- Scope: settings, schemas, test infrastructure, CI

### Summary
Resolved `ValidationError` and `ModuleNotFoundError` during test runs caused by stricter validation rules in Pydantic v2 and missing module resolution under `pytest`.

### Changes
- Replaced deprecated `class Config` with `model_config = SettingsConfigDict(...)` in `api/settings.py`
- Updated `RawInput` schema to use `model_config = ConfigDict(...)` and renamed `schema_extra` to `json_schema_extra`
- Confirmed all Pydantic settings and schemas are v2-compliant
- Removed invalid `pytest.ini` that included unsupported keys
- Added `PYTHONPATH=.` requirement to run tests successfully
- Verified no other use of deprecated `class Config` exists via recursive grep

### DevOps
- Updated CI pipeline to set `PYTHONPATH=.` at the job level
- Validated `api.main` imports resolve during CI and local runs
- Added documentation for testing procedure in `TESTING.md`

### Notes
- No functional changes to app logic or database interaction
- Project is now stable under Pydantic 2.11.5 with clean test execution in both local and CI environments



## [Feature] Add `/api/streamer/` endpoint for raw input simulation

- ID: API001
- Date: 2025-06-11
- Scope: api.streamer, schemas, tests/api

### Summary
Simulated POST endpoint `/api/streamer/` added to accept raw gesture/audio input with validation.

### Changes
- `StreamerInputSchema` added under `api/schemas/streamer.py`
- Endpoint mounted in `api/routes/streamer.py`
- Included in FastAPI app via `main.py`
- Basic test added at `tests/api/test_streamer.py` using httpx
- Fields: `user_id`, `session_id`, `timestamp`, `modality`, `intent_label`, `consent_given`
- Returns echo of validated input (mock behavior)

### DevOps
- `pytest.ini`: added `pythonpath = .`
- Installed `httpx` for test client

### Notes
- No DB writes yet
- Placeholder for future input capture logic



## [0.1.1] - 2025-06-11

## [Unreleased]

### Infra
- Unified FastAPI settings via `api/settings.py` using `get_settings()`
- Added `pyrightconfig.json` to suppress false-positive Pylance errors for env vars
- Verified `api/main.py` pulls settings correctly without duplication
- Structured `api/main.py` to support multiple entrypoints:
  - Production: `gunicorn -k uvicorn.workers.UvicornWorker api.main:app`
  - Development: `python api/main.py` or `uvicorn api.main:app --reload`


### Refactor
- Consolidated FastAPI environment configuration under `api/settings.py`
- Implemented `get_settings()` with Pydantic `BaseSettings` and `.env` loading
- Removed all direct `os.getenv` usage from FastAPI modules
- Ensured Pyright/Pylance compatibility with `pyrightconfig.json`

### Changed
- Unified FastAPI `Settings()` instantiation with `.env` loading
- CI fixed by ensuring `get_settings()` is available and structured
- PostgreSQL dev server restored and verified via `psql`
- `.env` file restored and values verified (including `DB_PASSWORD`, `SECRET_KEY`)

### Fixed
- VS Code Pylance warning about missing Settings arguments
- CI import error related to missing or mislocated settings modules



## [2025-06-11] – Local .env Integration Complete

### Fixed
- Resolved local `.env` loading for Django dev and VS Code tools.
- Verified `DB_PASSWORD` and other secrets now accessible via `load_dotenv()` in `config/settings/prod.py`.
- Confirmed `python manage.py migrate --settings=config.settings.prod` executes cleanly using Homebrew PostgreSQL.
- `.env` is now dev-usable and properly ignored from version control.

### Added
- Created `.env` manually in VS Code with correct credentials.
- Verified local database shell access via `manage.py dbshell`.
- Ensured `.env.example.prod` is tracked in Git for CI and contributor onboarding.

## [Unreleased] – 2025-06-11

### Infrastructure

- CI/CD: Restored GitHub Actions pipeline with PostgreSQL service and secret-based `DB_PASSWORD`.
- Dependency: Added `python-dotenv` to `requirements.txt` for `.env` support in local/dev environments.
- Branch Protections: Resolved merge block by adding `admin` to GitHub ruleset bypass list.
- Git Workflow: Rebased and synchronized `main` after push was rejected due to divergence.
- Validation: Verified presence of `ci.yml`, placeholder test suite, and working `pytest` setup.

### Recovery

- ⚠️ `.env` file was overwritten during branch switch; **actual project secrets not yet recovered**.
- Restored `.env.example` and confirmed version tracking for `.env.example.prod`.
- Manually reconstructed some local files; further recovery required for production `.env`.

### Documentation

- Versioning: Ensured `.env.example.prod` and `DEPLOYMENT.md` are committed.
- Logs: Documented merge flow issues, GitHub secret setup, and local environment inconsistencies.


### Changed
- Updated `.github/workflows/ci.yml` to use Postgres in CI with secrets for DB credentials.
- Set up `fix/postgres-requirement` branch to satisfy new GitHub repository rules (PRs required for main).
- Ensured `.env` is parsed via `load_dotenv()` in `config/settings/prod.py`.

### Fixed
- Prevented CI fallback to SQLite by enforcing presence of `DB_ENGINE` or CI-specific override.

------------------------------------------------------------
 ✅ Revisions to Dev Workflow and Contributor Guide
------------------------------------------------------------

- Rewrote DEV_WORKFLOW.md as a simplified contributor guide:
  - Removed staging branch references
  - Clarified local testing process
  - Emphasized CI/CD as the sole deploy path
  - Added structured module development flow

------------------------------------------------------------
 ✅ Revisions to setup.md
------------------------------------------------------------

- Updated virtual environment section to reflect server-only usage
- Rewrote local dev instructions for clarity
- Added FastAPI local URLs to dev server notes
- Added simulated message script usage for offline testing
- Clarified Git branching and PR policy

------------------------------------------------------------
 ✅ Sprint 1 Backlog Reconciliation
------------------------------------------------------------

- Compared current Sprint 1 backlog to real infrastructure needs
- Identified missing items and added:
  - Fix for CI `ImportError` (FastAPI settings import)
  - `.env.test` for FastAPI smoke testing
  - Latency script (`scripts/test_comm_latency.py`)
  - FastAPI port env vars (`UVICORN_PORT`) in `.env.example`
  - Optional Makefile/script improvements
  - Nginx example config block for FastAPI

------------------------------------------------------------
 ✅ Finalized Scope for Sprint 1
------------------------------------------------------------

- Reviewed and validated that all current tasks are aligned
- Determined new items are minor but high-leverage
- No further restructuring needed — ready to implement

============================================================
 END OF CHANGELOG
============================================================


## [2025-06-04] GitHub App-Based Auto-Deploy Pipeline Operational

### Added
- Created and installed GitHub App `A3CP Deployer` under `gesturelabs` org.
- Generated and securely stored a `.pem` private key for GitHub App authentication.
- Set appropriate **repository permissions** (`Contents: Read & Write`, `Metadata: Read`) for the app.
- Restricted app installation to `gesturelabs/a3cp` repository.
- Added the following repository secrets for deployment:
  - `GH_APP_ID` — GitHub App ID
  - `GH_APP_PRIVATE_KEY` — Base64-encoded private key for GitHub App
  - `VPS_HOST` — IP/domain of Hetzner server
  - `VPS_USER` — SSH username on VPS
  - `VPS_KEY` — Base64-encoded private SSH key for access

### Changed
- Replaced `deploy_key` SSH workflow with GitHub App token authentication via `tibdex/github-app-token@v2`.
- Updated `deploy.yml` GitHub Actions workflow:
  - Triggers on `push` to `main`
  - Authenticates as GitHub App
  - SSHs into Hetzner VPS and performs:
    - `git pull`
    - `pip install -r requirements.txt`
    - `python manage.py migrate`
    - `python manage.py collectstatic`
    - `sudo systemctl restart a3cp-gunicorn`

### Verified
- ✅ Workflow successfully triggers on push to `main`
- ✅ Authentication via GitHub App works
- ✅ VPS pulls latest code and redeploys cleanly

### Notes
- New workflow: **local → GitHub → Hetzner**
  - No need for developer SSH key management
  - GitHub App manages deployment auth
- GitHub Actions are now decoupled from contributor local machines

### Next Steps
- [ ] Remove unused deploy keys (if any remain)
- [ ] Rotate test/private credentials used during setup
- [ ] Add fallback or notification for failed deployments (e.g., Slack, email)
- [ ] Add rollback command to deployment script
- [ ] Document `deploy.yml` and app install process for future maintainers







## [2025-06-04] PostgreSQL Prep & Git Deployment Sync

### Changed
- Updated `config/settings/prod.py` to reference PostgreSQL via `.env`.
- Committed local changes made on Hetzner to Git (hotfixes to `prod.py`, `manage.py`, `CHANGELOG.md`).

### Infra
- Installed PostgreSQL 16 on Hetzner VPS.
- Created database `a3cp_pgsql` and user `a3cp_admin` with appropriate privileges.
- Updated `.env` with PostgreSQL credentials and confirmed visibility from `prod.py`.
- `python manage.py check` now passes, but `migrate` still fails due to `DATABASES` misconfiguration.

### Git & CI
- Aligned workflow to follow: local → GitHub → Hetzner.
- Initial GitHub push triggered CI/CD but **deploy job failed**.
- Deployment debugging pending.

### Outstanding
- PostgreSQL integration not yet functional — Django cannot connect.
- Deployment pipeline must be fixed to support automatic syncing from GitHub.


## [2025-06-03] Environment & Import Resolution Fixes

### Fixed
- Resolved `ModuleNotFoundError: No module named 'a3cp'` by ensuring correct working directory (`/opt/a3cp-app`) and `DJANGO_SETTINGS_MODULE` usage.
- Corrected Python path resolution and `sys.path` setup to include Django and local packages.
- Verified `manage.py` works with `config.settings.prod` without crashing.
- Confirmed all required packages are present in `/opt/a3cp-env/lib/python3.12/site-packages`.
- Validated `python manage.py check` and `shell` execute cleanly in production settings.

### Infra
- Ensured active virtual environment is `/opt/a3cp-env/`
- Confirmed Django 5.2.1 is installed and functional under Python 3.12.3

System is now import-clean, Django apps resolve properly, and shell/check commands execute without issue.


## [2025-06-02] - Environment & VS Code Remote Setup

### Added
- Connected to Hetzner VPS via VS Code Remote SSH.
- Verified connection using `~/.ssh/config` and key-based login.
- Opened remote folder and accessed `/opt/a3cp-app/` workspace.
- Activated Python virtual environment `a3cp-env` inside VS Code.

### Fixed
- Clarified SSH config setup and remote folder navigation.
- Ensured remote Python interpreter `/opt/a3cp-env/bin/python` is selected and active in VS Code.

✅ Environment now fully editable and runnable from VS Code over SSH.

## [2025-06-02] - Deployment Documentation Finalized

### Added
- Completed `docs/DEPLOYMENT.md` covering full production setup:
  - System requirements and firewall setup
  - Nginx config for Django and FastAPI endpoints
  - Gunicorn service configuration via systemd
  - HTTPS setup and certbot auto-renewal

✅ Task complete: `Document setup process in docs/DEPLOYMENT.md`

## [2025-06-02] - Routing Setup and Bug Fixes

### Added
- Created `pages` Django app under `apps/pages/`.
- Added basic views: `home`, `ui`, and `docs` returning simple `HttpResponse`s.
- Registered URL routes for `/`, `/ui/`, and `/docs/` in `apps/pages/urls.py`.
- Included `apps.pages.urls` in the root `config/urls.py`.

### Fixed
- Corrected app label in `PagesConfig.name` from `app.pages` to `apps.pages`.
- Resolved `ModuleNotFoundError: No module named 'config_tmp'` by restoring correct `DJANGO_SETTINGS_MODULE` to `'config.settings'`.
- Resolved duplicate app label error (`Application labels aren't unique, duplicates: pages`).

### Deployment
- Restarted services using:
  - `sudo systemctl restart a3cp-gunicorn` — restart the Django app server.
  - `sudo systemctl restart nginx` — restart the Nginx web server.
- Verified:
  - Gunicorn status via `systemctl status a3cp-gunicorn`.
  - Page routing via manual browser testing.

✅ Task complete: `Route all other pages via Django + HTMX (/ /ui /docs)`


## 2025-05-29 — Initial Production Server Setup (Hetzner VPS)

### Infrastructure Setup
- ✅ Created new SSH keypair (`hetzner_key`, `hetzner_key.pub`) and registered for secure access
- ✅ Provisioned new Hetzner VPS with IP `157.180.43.78`
- ✅ Connected to server via SSH using new key
- ✅ Upgraded system and kernel; rebooted into new kernel (6.8.0-60-generic)
- ✅ Enabled UFW firewall: allow only SSH (port 22), deny other incoming traffic

### Domain Configuration
- ✅ Pointed domain `gesturelabs.org` and `www.gesturelabs.org` to server IP
- ✅ Cleaned existing DNS records, replaced with A records
- ✅ Verified DNS propagation with `dig` and fallback nameservers (e.g. `@8.8.8.8`)

### Nginx + HTTPS Setup
- ✅ Installed and started Nginx; verified default Nginx welcome page at:
  - http://gesturelabs.org
- ✅ Installed Certbot and obtained Let’s Encrypt SSL certificates
- ✅ HTTPS successfully enabled for:
  - https://gesturelabs.org
  - https://www.gesturelabs.org
- ✅ Verified `certbot renew --dry-run` passes successfully
- ✅ Verified automatic renewal via `certbot.timer` is active

### Python Web Server (Gunicorn)
- ✅ Installed `python3-venv` and created `/opt/a3cp-env` virtual environment
- ✅ Installed Gunicorn inside venv
- ✅ Verified Gunicorn version: `23.0.0`

---

## Outstanding Tasks

- [ ] Route `/api/infer/` to FastAPI using Nginx reverse proxy
- [ ] Build and deploy initial Django + FastAPI apps
