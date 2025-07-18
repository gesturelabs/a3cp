# Submodule: retraining_scheduler

## Purpose
Determines when a user-specific model requires retraining based on defined policy triggers,
such as sample volume, clarification rate, or staleness. It periodically analyzes logs and
metadata to decide whether training should be invoked and signals the `model_trainer` with
a retraining request.

## Responsibilities
- Monitor per-user, per-modality logs for:
  - New labeled examples (`recorded_schemas`)
  - Clarification and correction frequency (`feedback_log`)
  - Model age (`model_registry`)
- Compare observed metrics against policy thresholds (e.g., min samples, max clarification rate, max age)
- Trigger training by issuing a retraining request to `model_trainer` with relevant metadata
- Optionally log retraining decisions and their trigger rationale for auditability

## Not Responsible For
- Training models (handled by `model_trainer`)
- Writing to the `model_registry` (handled by `model_trainer`)
- Labeling or editing user feedback
- Storing training samples or schema records

## Inputs
- recorded_schemas
  - Used to count new examples since the last model training event for a given (`user_id`, `modality`)
  - Includes feature references, vector version, and input metadata

- feedback_log
  - Used to compute clarification rates, label correction frequency, and trust level of classifier outputs

- model_registry
  - Queried for latest training timestamp, vector version, and training config per user/modality

## Outputs
- model_trainer
  - Receives retraining request messages containing:
    - `user_id`
    - `modality`
    - `retrain_reason`
    - `latest_model_version` (optional)
    - `policy_config_version`

Note: The `model_trainer` is responsible for fetching data from `recorded_schemas` and
`user_profile_store`. The `retraining_scheduler` only determines when to initiate retraining.

## Retraining Policy Fields
Defined as a config dictionary or external JSON/YAML file.

| Field                  | Type    | Example | Description                                       |
|------------------------|---------|---------|---------------------------------------------------|
| min_new_samples        | integer | 50      | Minimum number of new schema records              |
| max_clarification_rate | float   | 0.15    | Maximum tolerated clarification frequency         |
| max_days_since_train   | integer | 30      | Maximum age of model in days before retraining    |

These can be defined globally or per modality.

## Trigger Logic
For each (`user_id`, `modality`) pair:
- Count new samples since last model in `recorded_schemas`
- Calculate clarification rate from `feedback_log`
- Compute model age from `model_registry`

If any of the configured thresholds are exceeded, a retraining request is sent to `model_trainer`.

Example logic:

if new_samples >= min_new_samples:
    trigger("New sample threshold")
elif clarification_rate > max_clarification_rate:
    trigger("High clarification rate")
elif model_age_days > max_days_since_train:
    trigger("Model age exceeded")

## Runtime Considerations
- Scheduler may be triggered periodically (e.g., daily via cron) or in response to feedback events
- Must debounce triggers to avoid redundant training requests for the same user/modality
- Must support safe concurrent access to log files or database rows
- May support dry-run or audit mode for simulation and testing

## Retraining Request Payload (to `model_trainer`)

{
  "user_id": "abc123",
  "modality": "gesture",
  "retrain_reason": "High clarification rate (0.23 > 0.15)",
  "latest_model_version": "gesture-abc123-20250701",
  "policy_config_version": "v1.0.0"
}

## Logging & Audit (Optional)
The scheduler may log retraining events to a structured file:

  logs/system/retraining_log.jsonl

Each log entry should include:
- user_id
- modality
- timestamp
- trigger_reason
- num_new_samples
- clarification_rate
- model_version_before
- policy_config_version

## Integration Notes
- To model_trainer: Sends JSON retraining signal message
- From recorded_schemas: Counts new training records
- From feedback_log: Analyzes interaction quality
- From model_registry: Finds most recent model version + timestamp

## References
- SCHEMA_REFERENCE.md – defines message fields, feedback structure, and vector versioning
- model_registry/README.md – model version metadata and queryable format
- feedback_log/README.md – label correction and clarification tracking
- model_trainer/README.md – expected inputs and outputs
- retraining_policy.json – configurable thresholds for retraining trigger

## Development TODOs
- [ ] Implement per-modality policy loading from JSON
- [ ] Create retraining trigger audit log format
- [ ] Add dry-run simulation mode for testing policy sensitivity
- [ ] Debounce retraining requests to avoid redundant training
- [ ] Unit tests for each policy branch (sample volume, clarification rate, age)

## Open Questions
- Should retraining be capped per day/week to avoid overfitting?
- Should user-specific retraining frequency be tracked and penalized if too frequent?
- How should clarification triggers be normalized for low-frequency users?
