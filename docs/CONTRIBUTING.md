# Contributing to A3CP

Thank you for your interest in contributing to A3CP — a collaborative project supporting adaptive communication for people with complex needs. We welcome contributions in code, design, documentation, and testing.

---

## 1. Code of Conduct

Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## 2. Getting Started

### Clone the repository
```bash
git clone git@github.com:gesturelabs/a3cp.git
cd a3cp
```

> Note: SSH key access may be required. Ask an admin to add your key if needed.

### Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Copy environment variables
```bash
cp .env.example .env
# Edit as needed for your environment
```

---

## 3. Running the System

### FastAPI (Inference Service)
```bash
./scripts/manage.sh dev-api
```

### Django (Admin + Upload UI)
```bash
./scripts/manage.sh dev-django
```

---

## 4. Testing and Linting

### Run all tests
```bash
./scripts/manage.sh test
```

### Run lint checks
```bash
./scripts/manage.sh lint
```

### Auto-format code
```bash
./scripts/manage.sh format
```

> Tip: You can also use `pytest`, `black .`, or `flake8 .` directly if preferred.

---

## 5. Making Contributions

### Branch naming
- `feature/<topic>` for new features
- `fix/<bug>` for bugfixes
- `docs/<topic>` for documentation

### Commit messages
Use imperative tone and describe what you did:
```text
Add /api/sound/infer/ endpoint and test stub
```
## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
    Install pre-commit hooks:
pre-commit install
Run on all files to verify:
    pre-commit run --all-files


### Pull requests
- Base branch: `main`
- Include tests for new features
- Run `./scripts/manage.sh test` and `lint` before submitting
- Link to related issues if applicable

---

## 6. Project Structure (Simplified)
```text
api/                # FastAPI app and schema definitions
apps/               # Django project and apps
scripts/            # Helper scripts for dev, deployment, management
tests/              # All unit and integration tests
.env                # Environment variables (not committed)
requirements.txt    # Python dependencies
```

---

## 7. Non-Code Contributions

We welcome help with:
- UI/UX design and accessibility testing
- Symbol set expansion and data modeling
- Community evaluation and user testing
- Translating documentation or training materials

---

## 8. Getting Help
- Open an issue on GitHub
- Reach out to the maintainers
- Use the contact form on [gesturelabs.org](https://gesturelabs.org) (if available)

---

## 9. Acknowledgments
A3CP is developed by GestureLabs and partners under an open infrastructure model with support from research institutions and community contributors.
