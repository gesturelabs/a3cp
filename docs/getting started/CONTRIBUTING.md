============================================================
Contributing to A3CP
============================================================

Thank you for your interest in contributing to A3CP — a collaborative
project supporting adaptive communication for people with complex needs.

We welcome contributions in code, design, documentation, and testing.

------------------------------------------------------------
1. Code of Conduct
------------------------------------------------------------

Please read and follow our CODE_OF_CONDUCT.md:
https://github.com/gesturelabs/a3cp/blob/main/CODE_OF_CONDUCT.md

------------------------------------------------------------
2. Getting Started
------------------------------------------------------------

Clone the repository:
    git clone git@github.com:gesturelabs/a3cp.git
    cd a3cp

Note: SSH access may be required. Ask an admin if needed.

Then follow the Developer Setup Guide:
    docs/DEV_SETUP.md

Includes:
    - Python virtualenv setup
    - Installing dependencies
    - Creating .env file
    - Running Django + FastAPI locally
    - Running tests and linters
    - Using scripts/manage.sh and Makefile

------------------------------------------------------------
3. Making Contributions
------------------------------------------------------------

Branch naming:
    feature/<topic>    for new features
    fix/<bug>          for bugfixes
    docs/<topic>       for documentation

Commit messages:
    Use imperative tone:
    e.g., Add /api/sound/infer/ endpoint and test stub

Pull requests:
    - Base branch: main
    - Include tests for new features
    - Run tests and pre-commit hooks before submitting
    - Link to issues where relevant

------------------------------------------------------------
4. Project Structure (Simplified)
------------------------------------------------------------

    api/               FastAPI endpoints and schema logic
    apps/              Django apps (admin, upload, etc.)
    scripts/           Dev and deployment helpers
    schemas/           Pydantic runtime validation models
    interfaces/        JSON-based schema specs
    tests/             Test suite
    requirements*.txt  Dependency files
    .env               Local environment config (not committed)

------------------------------------------------------------
5. Non-Code Contributions
------------------------------------------------------------

We also welcome contributions in:
    - UI/UX and accessibility
    - Symbol design and modeling
    - User evaluation and feedback
    - Documentation translation

------------------------------------------------------------
6. Getting Help
------------------------------------------------------------

    - Open an issue on GitHub
    - Contact a maintainer
    - Or reach out via gesturelabs.org (if public form available)

------------------------------------------------------------
7. Acknowledgments
------------------------------------------------------------

A3CP is developed by GestureLabs and partners, with support
from researchers, educators, and disability community stakeholders.
