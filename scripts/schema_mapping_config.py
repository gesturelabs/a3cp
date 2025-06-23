SCHEMA_MAPPING = {
    "a3cp_message": {
        "schema": "interfaces/a3cp_message.schema.json",
        "examples": ["docs/modules/input_broker/sample_input.json"],
    },
    "raw_action_record": {
        "schema": "interfaces/raw_action_record.schema.json",
        "examples": ["docs/modules/raw_input_log/sample_input.json"],
    },
    "inference_trace": {
        "schema": "interfaces/inference_trace.schema.json",
        "examples": ["docs/modules/confidence_evaluator/sample_output.json"],
    },
    "clarification_event": {
        "schema": "interfaces/clarification_event.schema.json",
        "examples": ["docs/modules/clarification_planner/sample_output.json"],
    },
}
