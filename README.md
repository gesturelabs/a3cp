# A3CP: Ability-Adaptive Augmentation for Communication Personalisation

**A3CP** is an open, modular framework for augmentative communication designed for individuals with complex communication needs who are not well served by conventional AAC systems. Funded by The Open University and developed in collaboration with GestureLabs e.V., A3CP prioritizes adaptability, explainability, and long-term personalization.

## 1. Introduction

A3CP addresses the needs of users—such as children with cerebral palsy or adults with autism spectrum disorder—whose expressive behaviors (gestures, vocalizations, context-specific cues) do not map cleanly onto traditional AAC symbols or fixed-button interfaces.

At its core is the **CARE Engine** (Context-Aware Response Engine), which fuses multimodal input (gesture, sound, context), infers communicative intent, and generates symbolic, spoken, or textual output. A3CP scaffolds user expression over time, adapting to both the communicator and their caregivers.

> ⚠️ A3CP is released under a **Creative Commons BY-NC 4.0** license. Commercial use is not permitted.

## 2. System Goals

- Support naturalistic interaction via speech, text, or symbol output.
- Scaffold communication development from early intents to complex expression.
- Adapt to each user's motor, sensory, and cognitive profile.
- Allow per-user training, feedback, and model personalization.
- Enable caregiver participation in labeling, clarification, and correction.

## 3. Architecture Highlights

- **Modular Design:** Each modality (gesture, sound, context) is handled by isolated processors.
- **Edge-Compatible:** Designed for future deployment on Jetson Nano, Raspberry Pi, and other local devices.
- **Rule-First Reasoning:** Transparent, score-based fusion with fallback LLM clarification.
- **CARE Engine:** Coordinates fusion, memory, clarification, and multimodal output.

See the [Architecture Guide](docs/ARCHITECTURE.md) and [Deployment Plan](docs/DEPLOYMENT.md) for details.

## 4. Demonstrator Features

The MVP interface provides:

- Real-time webcam/audio capture
- Caregiver labeling and feedback loop
- Per-user model training with Hugging Face integration
- Symbolic/clarified output and confidence display

Pages:
- `/` – Landing page with CTA and visual overview
- `/ui/modules/` – System diagram and module descriptions
- `/ui/demonstrator/` – Four-tab interface (Record, Visualize, Train, TryIt)
- `/ui/docs/` – Schema and API reference

## 5. Project Structure
- apps/ # Django apps (streamer, processors, CARE engine, UI)
- api/ # FastAPI inference endpoints
- schemas/ # Internal message and log schemas (pydantic)
- interfaces/ # External schema definitions (JSON Schema)
- logs/ # Session and input logs (JSONL + SQLite)
- deploy/ # Gunicorn/Nginx service setup
- docs/ # Full documentation suite (architecture, deployment, API)
- tests/ # Pytest test suite (mirrors app layout)


## 6. License and Use

This project is licensed under **[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)**. You may use, adapt, and share the code **for non-commercial purposes only**. Commercial use requires explicit permission from The Open University and GestureLabs e.V.

See `LICENSE` for full terms.


## 7. Contributing

Community contributions are welcome, especially from those working in academic, nonprofit, or personal-use contexts.

Before contributing, please ensure:

- You are using the latest version of the repository.
- Your code is clean, tested, and documented where appropriate.
- You follow the project architecture and directory conventions.

We enforce code quality using `pre-commit` hooks. These will automatically check formatting and linting before each commit.

### Git Hook Setup

1. Install developer dependencies:

    pip install -r requirements-dev.txt

2. Install pre-commit hooks:

    pre-commit install

This will enable automatic checks before every commit. The following tools are applied:

- black: code formatting
- ruff: linting and basic style enforcement
- isort: import sorting

### Manual Checks

To manually run all checks on your current working directory:

    pre-commit run --all-files

Please ensure all hooks pass before pushing code.

A full CONTRIBUTING.md with more guidelines is in preparation.



## 8. Status

- ✅ Hetzner deployment active
- ✅ Secure API routing
- 🔧 MVP TryIt interface in progress
- 🔜 CARE Engine training + feedback loop integration

## 9. Contacts

- Lead Developer: Dmitri Katz (`dmitrikatz23@gmail.com`)
- Maintainer: [GestureLabs e.V.](https://gesturelabs.org)
- Affiliated Institutions: The Open University, JKU Linz
