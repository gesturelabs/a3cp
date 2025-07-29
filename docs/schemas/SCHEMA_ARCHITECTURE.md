===============================================================================
 A3CP SCHEMA ARCHITECTURE SPECIFICATION — v1.1
-------------------------------------------------------------------------------
 Purpose:
   Define the rules for managing one-to-many output schemas, example generation,
   and schema documentation consistency across all A3CP modules.
===============================================================================

[1] SCHEMA STRUCTURE CONSTRAINTS
-------------------------------------------------------------------------------
- Each module must define exactly ONE input and ONE output example.
- Examples must conform exactly to the module’s Pydantic schema.
- Output schemas must be designed to satisfy ALL downstream consumers.
- No per-target branching schemas (e.g. one output must work for all receivers).
- Optional fields must be omitted unless semantically meaningful.
- Avoid wrapper nesting (e.g. "event") unless explicitly required.
- Nested objects are allowed only when:
    * Grouping semantically related fields (e.g. clarification.*, memory.*, context.*)
    * Defined via dedicated submodels and schema validation

[2] ONE-TO-MANY OUTPUT DESIGN RULES
-------------------------------------------------------------------------------
- Modules with multiple "outputs_to" (e.g. input_broker) must:
    * Emit a unified superset output schema
    * Include all fields required by ALL receivers
    * Clearly document which field is used by which receiver (in .schema.md)
- No module may emit multiple different schema variants to different receivers.
- Fields used by only one downstream module must be marked as Optional.
- Superset schemas must include a Module Usage Matrix in `.schema.md` describing:
    * Which module reads/writes which fields
    * Lifecycle responsibility for each field group

[3] EXAMPLE FILES AND STRUCTURE
-------------------------------------------------------------------------------
For each module, store files at:

  schemas/<module_name>/<module_name>_input_example.json
  schemas/<module_name>/<module_name>_output_example.json
  schemas/<module_name>/<module_name>_schema.md

These must include:

  - Input/Output example that matches Pydantic model exactly
  - .schema.md describing:
      * Purpose
      * Inputs_from and Outputs_to
      * Field-by-field breakdown
      * Version, if applicable
      * Module Usage Matrix (required for superset schemas)

[4] FUTURE EXTENSIONS (OPTIONAL FOR NOW)
-------------------------------------------------------------------------------
- Add schema versioning: e.g. "v1", "v2", etc.
- Implement schema deprecation rules:
    * Fields must be marked deprecated before removal
    * Field removals require MAJOR version bump
- Enforce schema linting in CI:
    * Verify presence and location of input/output/example/schema files
    * Validate flatness and structural conformity of schema
    * Check 1:1 example-schema alignment via runtime tests
    * Ensure field optionality matches usage across consumers
    * Validate that nested objects follow approved grouping patterns
    * Flag irrelevant fields in output examples (not used by outputs_to)

===============================================================================
