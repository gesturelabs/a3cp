#!/usr/bin/env bash

set -e  # Exit on first error
COMMAND=$1

# Optional: activate .venv if not already active
if [[ -z "$VIRTUAL_ENV" && -d ".venv" ]]; then
  source .venv/bin/activate
fi

case "$COMMAND" in
  dev-api)
    echo "🚀 Starting FastAPI dev server (api.main:app) on port 8001..."
    uvicorn api.main:app --reload --port 8001
    ;;

  dev-django)
    echo "🧩 Starting Django dev server on port 8000..."
    python manage.py runserver 0.0.0.0:8000
    ;;

  test)
    echo "✅ Running all tests..."
    pytest
    ;;

  lint)
    echo "🔍 Running flake8 and black..."
    flake8 . && black --check .
    ;;

  format)
    echo "🧼 Formatting code with black..."
    black .
    ;;

  clean-pyc)
    echo "🧹 Removing Python cache files..."
    find . -type f -name '*.py[co]' -delete
    find . -type d -name '__pycache__' -delete
    ;;

  docker-build)
    echo "🐳 Building Docker image as 'a3cp-app'..."
    docker build -t a3cp-app .
    ;;

  docs)
    echo "📚 Building documentation with MkDocs..."
    mkdocs build
    ;;

  "" | help | *)
    echo "Usage: $0 {dev-api|dev-django|test|lint|format|clean-pyc|docker-build|docs|help}"
    exit 1
    ;;
esac
