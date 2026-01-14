# Module: output_planner

## Purpose
The `output_planner` module selects the appropriate output modality (e.g., speech, text, symbol) to communicate a finalized intent. It packages the expanded phrase for dispatch to the AAC user interface, ensuring compatibility with user preferences and device capabilities.

## Why It Matters
This module ensures that communicative outputs are accessible and effective for the user. By enforcing user-configured modality preferences and adapting to device constraints, it plays a central role in delivering understandable, inclusive AAC content across different environments.

## Responsibilities
- Select the output modality (e.g., "speech", "text", "symbol") based on user profile and system context
- Package and dispatch the `output_phrase` to the AAC UI layer
- Enforce user preferences (e.g., mute mode, symbol-only output)
- Allow multimodal redundancy (e.g., symbol + text) when configured
- Log output decisions for review and traceability

## Not Responsible For
- Determining the user’s intent (`final_decision`)
- Generating natural-language phrases (handled by `output_expander`)
- Executing TTS synthesis, rendering text, or displaying symbols

## Inputs
- `output_phrase`: the expanded communicative phrase
- `final_decision`: the confirmed intent label
- `output_type`: must be "intent"
- `user_profile`: includes modality preferences and restrictions
- `system_config`: optional device-specific capabilities
- `timestamp`, `user_id`, `session_id`: for logging and traceability

## Outputs
- `output_mode`: selected delivery method ("speech", "text", "symbol", or combinations)
- Dispatched output payload to the UI rendering layer
- Log entry including: `timestamp`, `user_id`, `session_id`, `intent_label`, `output_mode`, `output_phrase`

## CARE Integration
The `output_planner` is triggered after the `output_expander` generates a phrase from the `final_decision`. It determines how this phrase should be delivered and routes it to the AAC interface. This marks the final step in the CARE loop for output delivery.

## Functional Requirements
- F1. Select supported output modality based on user profile and available configuration
- F2. Respect user restrictions (e.g., no audio output)
- F3. Handle fallback logic if preferred modality is unsupported
- F4. Allow multimodal dispatch (e.g., text + symbol) when redundancy is enabled
- F5. Log each decision with full metadata for auditability

## Non-Functional Requirements
- NF1. Complete modality selection and dispatch in under 100ms
- NF2. Fail gracefully with default output if no preferred modality is available
- NF3. Ensure logs are complete, consistent, and traceable by session and user
- NF4. Avoid redundant dispatch unless explicitly configured

## Developer(s)
Unassigned

## Priority
High

## Example Files
- [sample_input.json](./sample_input.json)
- [sample_output.json](./sample_output.json)
- [schema.json](./schema.json)
