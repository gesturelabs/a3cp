#!/usr/bin/env python3
import os
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

# Load .env file into os.environ
load_dotenv()

REQUIRED_VARS = [
    "DEBUG",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "DJANGO_SETTINGS_MODULE",
    "PYTHONUNBUFFERED",
    "DB_ENGINE",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
]

OPTIONAL_VARS = [
    "INFER_API_URL",
    "UVICORN_PORT",
    "FASTAPI_HOST",
    "CLOUD_STORAGE_KEY",
    "CLOUD_STORAGE_SECRET",
    "LOG_LEVEL",
    "STATIC_ROOT",
    # "GUNICORN_PORT",
]


def load_env_file(env_path: Path):
    key_occurrences = defaultdict(int)
    malformed = []

    if not env_path.exists():
        print(f"WARNING: .env file not found at {env_path}")
        return [], []

    with env_path.open("r") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                malformed.append((i, line))
                continue
            key, _ = line.split("=", 1)
            key_occurrences[key.strip()] += 1

    duplicates = [k for k, count in key_occurrences.items() if count > 1]
    return duplicates, malformed


def check_env():
    env_path = Path(".env")
    duplicates, malformed = load_env_file(env_path)

    if duplicates:
        print("ERROR: Duplicate keys in .env file:")
        for key in duplicates:
            print(f"  - {key}")
        sys.exit(1)

    if malformed:
        print("ERROR: Malformed lines in .env file:")
        for lineno, content in malformed:
            print(f"  Line {lineno}: {content}")
        sys.exit(1)

    missing_required = [var for var in REQUIRED_VARS if not os.getenv(var)]
    missing_optional = [var for var in OPTIONAL_VARS if not os.getenv(var)]

    if missing_required:
        print("ERROR: Missing required environment variables:")
        for var in missing_required:
            print(f"  - {var}")
        sys.exit(1)

    print("All required environment variables are set.")

    if missing_optional:
        print("\nWARNING: The following optional variables are not set:")
        for var in missing_optional:
            print(f"  - {var}")


if __name__ == "__main__":
    check_env()
