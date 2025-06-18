# Development Flow

This document describes the branching strategy, review policy, and CI integration rules for the A3CP repository.

## Branching Strategy

- **`main`**:  
  This is the stable release branch. All production deployments are triggered from `main`. Only tested and reviewed code should end up here.

- **Feature Branches**:  
  All work should be developed on a separate feature branch. Use the following naming convention:

feature/<short-description>

Example:

feature/train-infer-model


- **Pull Requests**:  
Feature branches must be merged via a pull request (PR) into `main`. Each PR should:
- Have a clear title and description
- Reference relevant issues, if applicable
- Trigger CI checks (lint, tests, environment validation)

## Reviews & Permissions

- **Repository Admin (e.g., @dmitrikatz)**:
- Can push directly to `main` (bypass rules)
- Can merge PRs without reviews
- Responsible for reviewing PRs from others

- **Contributors**:
- Must use a feature branch
- Must create PRs to `main`
- Cannot push directly to `main`
- PRs require approval before merge

## CI/CD Integration

- GitHub Actions are triggered on `push` and `pull_request` events to `main`
- The following CI steps must pass before a PR is eligible for merge:
- Dependency installation
- Environment variable validation (`validate_env.py`)
- Django system checks
- Pytest (unit and integration tests)
- Linting (via separate workflow, e.g. `lint.yml`)

## Deployment

- Production deployment is automatic on `main` branch push via `deploy.yml`
- Admin can trigger deploys by merging to `main` or pushing directly

## Notes

- For testing features that require HTTPS or production integration (e.g. OAuth, FastAPI inference), Admin may push temporary work directly to `main` with clear commit messages. This exception should be used judiciously and followed by cleanup or PR-based refactor when feasible.

---

_Last updated: 2025-06-18_
