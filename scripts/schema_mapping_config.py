SCHEMA_MAPPING = {
    "a3cp_message": {
        "source": "schemas/source/a3cp_message.py",
        "schema": "schemas/outputs/a3cp_message.schema.json",
        "examples": [
            "schemas/examples/a3cp_message/sample_input.json",
            "schemas/examples/a3cp_message/sample_output.json",
        ],
    },
    "raw_action_record": {
        "source": "schemas/source/raw_action_record.py",
        "schema": "schemas/outputs/raw_action_record.schema.json",
        "examples": [
            "schemas/examples/raw_action_record/sample_input.json",
            "schemas/examples/raw_action_record/sample_output.json",
        ],
    },
    "inference_trace": {
        "source": "schemas/source/inference_trace.py",
        "schema": "schemas/outputs/inference_trace.schema.json",
        "examples": [
            "schemas/examples/inference_trace/sample_input.json",
            "schemas/examples/inference_trace/sample_output.json",
        ],
    },
    "clarification_event": {
        "source": "schemas/source/clarification_event.py",
        "schema": "schemas/outputs/clarification_event.schema.json",
        "examples": [
            "schemas/examples/clarification_event/sample_input.json",
            "schemas/examples/clarification_event/sample_output.json",
        ],
    },
}
