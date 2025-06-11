# DEV_WORKFLOW.md — A3CP Contributor Development Workflow (2025)

This document describes how contributors should develop, test, and submit modules to the A3CP platform. The system uses a message-based architecture with clearly defined schemas. Contributors test modules locally and submit PRs to `main`. There is no staging server or staging branch.

====================================================================
 OVERVIEW
====================================================================

- A3CP is built from modular components:
  - Gesture Processor
  - Sound Processor
  - Contextual Profiler
  - CARE Engine (Clarification Planner)

- Each module:
  - Accepts a structured input message
  - Returns a structured output message
  - Uses `pydantic` for schema validation
  - Is testable locally with scripts and unit tests

- All production deployment is handled via GitHub Actions after PR review.

====================================================================
 CONTRIBUTOR WORKFLOW
====================================================================

1. **Fork and clone the repository**

2. **Create a feature branch**

git checkout -b feat/<your-module-name>


3. **Write your module**
- Place your logic in `modules/` or `api/`
- Use existing schemas or define new ones in `schemas/`

4. **Write unit tests**
- Place tests in `tests/<your-module>/`
- Use `pytest`

5. **Optionally write a simulation script**
- Create `simulate.py` to run your module with example input
- Load test payloads from `tests/data/`

6. **Test everything locally**

pytest tests/<your-module>/
python simulate.py --input tests/data/example_input.json


7. **Commit and push your changes**

git add .
git commit -m "feat: add <your module>"
git push origin feat/<your-module-name>


8. **Open a pull request to `main`**
- A reviewer will verify your code, tests, and schema usage

9. **If approved, the PR is merged**
- GitHub Actions deploys the updated app to production automatically

====================================================================
MODULE STRUCTURE EXAMPLE
====================================================================

Example for `contextual_profiler`:

modules/
contextual_profiler.py ← your logic

schemas/
context.py ← input/output message schemas

tests/
contextual_profiler/
test_logic.py ← unit tests
test_integration.py ← end-to-end checks

tests/data/
example_input.json ← sample input

simulate/
simulate_context.py ← optional test runner


====================================================================
 LOCAL DEVELOPMENT ENVIRONMENT
====================================================================

- Use `.env.development` for local variables
- Use `pytest` to run tests
- Do **not** push `.env` files or test artifacts to the repo
- Do **not** deploy anything yourself — CI/CD handles deployment

====================================================================
 CI AND DEPLOYMENT
====================================================================

- All production code lives on the `main` branch
- GitHub Actions requires:
  - All tests must pass
  - Code must be reviewed and approved
- After merge, `main` is automatically deployed to:

https://gesturelabs.org


====================================================================
SUPPORT
====================================================================

- GitHub Issues: https://github.com/gesturelabs/a3cp/issues
- Maintainer contact: Dmitri Katz
- Slack/Matrix: TBD

====================================================================
END OF CONTRIBUTOR WORKFLOW
====================================================================
