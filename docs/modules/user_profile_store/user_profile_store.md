# Module: user_profile_store

## Purpose
Stores per-user personalization data, including vocabulary preferences, output modes, clarification behavior, and partner-sourced configuration. Enables the system to tailor communication experiences to individual user needs, while preserving both human input and machine adaptation.

## Why It Matters
Personalized interaction is essential in AAC systems. Users differ in vocabulary, comprehension thresholds, preferred output formats, and required scaffolding. The `user_profile_store` centralizes these elements, providing a single, trusted interface for modules that depend on user-specific configurations.

## Responsibilities
- Store static caregiver-defined settings (e.g., preferred intents, output mode)
- Maintain editable vocabulary mappings for gestures, sounds, etc.
- Track behavioral parameters (e.g., clarification threshold, verbosity)
- Permit machine-written updates in a structured and auditable manner
- Provide read-only access to modules during runtime inference
- Support UI interaction for caregiver updates

## Not Responsible For
- Real-time adaptation based on interaction outcomes (handled by `memory_interface`)
- Direct classifier label encoding (handled by `model_registry`)
- Clarification logic or inference fusion
- Final decision-making in the CARE loop

## Inputs
- Partner/caregiver-edited preferences and mappings
- Machine-inferred settings or intent usage stats (via trusted update routines)

## Outputs
- Read-only views for runtime modules
- Vocabulary definitions for training and compilation
- Behavioral preferences consumed by clarification and output modules
- Profile snapshot for audit logging or export

## CARE Integration
Provides user-specific configuration to multiple modules:
- Supplies behavioral parameters to `clarification_planner`, `output_expander`, and `llm_clarifier`
- Enables `model_trainer` to access up-to-date vocabularies during retraining
- Supports UI-based review and override of system-inferred preferences

## Functional Requirements
- F1. Store editable preferences and vocab mappings per user
- F2. Track settings such as default output mode, clarification thresholds, and verbosity
- F3. Expose APIs for secure machine updates with provenance tagging
- F4. Allow profile export/import for use in training and deployment
- F5. Support versioned schema for auditability and compatibility

## Non-Functional Requirements
- NF1. Must support concurrent read access by multiple inference modules
- NF2. All updates must be append-only and auditable
- NF3. UI changes must be instantly reflected in dependent modules
- NF4. Profile data must persist across sessions and deployments
- NF5. Sensitive fields must be access-controlled and pseudonymized when logged

## Developer(s)
Unassigned

## Priority
High – essential for personalization, auditability, and human-in-the-loop adaptation

## Example Files
- examples/user_profile_preference.json
- examples/system_inferred_profile_patch.json
- examples/vocab_mapping_input.json
