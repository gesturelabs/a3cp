# scripts/generate_schemas_from_master.py
import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Type

from pydantic import BaseModel

SCHEMAS_DIR = Path("schemas")
SCHEMA_BASE_URL = "https://gesturelabs.org/schemas/"


def find_schema_files():
    schema_targets = []
    for folder in SCHEMAS_DIR.iterdir():
        if folder.is_dir():
            expected_file = folder / f"{folder.name}.py"
            if expected_file.exists():
                schema_targets.append((folder.name, folder, expected_file))
            else:
                print(f"⚠️  Expected {expected_file.name} in {folder} not found.")
    return schema_targets


def import_model_module(py_file: Path, folder_name: str):
    module_name = f"{folder_name}.{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {py_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_wrapped_schema(model_cls: Type[BaseModel], folder_name: str) -> dict:
    inner_schema = model_cls.model_json_schema()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URL}{folder_name}_schema.json",
        "title": f"{folder_name.replace('_', ' ').title()} Schema",
        "description": f"Schema for {folder_name} input and output messages.",
        "type": "object",
        "$defs": {model_cls.__name__: inner_schema},
    }


def generate_schema_file(model_cls: Type[BaseModel], folder: Path, folder_name: str):
    output_path = folder / f"{folder_name}_schema.json"

    try:
        wrapped = generate_wrapped_schema(model_cls, folder_name)
        output_path.write_text(json.dumps(wrapped, indent=2))
    except Exception as e:
        print(f"❌ Failed to generate schema for {folder_name}: {e}", file=sys.stderr)


def generate_input_example(model_cls: Type[BaseModel], folder: Path, folder_name: str):
    try:
        if hasattr(model_cls, "example_input"):
            input_func = model_cls.example_input  # type: ignore[attr-defined]
            if not callable(input_func):
                print(
                    f"⚠️  example_input exists but is not callable in {model_cls.__name__}"
                )
                return

            input_data = input_func()

            # Normalize to dict if model instance is returned
            if isinstance(input_data, BaseModel):
                input_data = input_data.model_dump()
            elif not isinstance(input_data, dict):
                print(
                    f"⚠️  example_input for {model_cls.__name__} did not return a dict or BaseModel"
                )
                return

            input_path = folder / f"{folder_name}_input_example.json"
            input_path.write_text(json.dumps(input_data, indent=2, sort_keys=True))
            print(f"✅ Regenerated input example: {input_path.name}")
        else:
            print(f"⚠️  No example_input method found in {model_cls.__name__}")
    except Exception as e:
        print(
            f"❌ Error generating input example for {folder_name}: {e}", file=sys.stderr
        )


def generate_output_example(model_cls: Type[BaseModel], folder: Path, folder_name: str):
    try:
        if hasattr(model_cls, "example_output"):
            output_func = model_cls.example_output  # type: ignore[attr-defined]
            if not callable(output_func):
                print(
                    f"⚠️  example_output exists but is not callable in {model_cls.__name__}"
                )
                return

            output_data = output_func()

            # Normalize to dict if model instance is returned
            if isinstance(output_data, BaseModel):
                output_data = output_data.model_dump()
            elif not isinstance(output_data, dict):
                print(
                    f"⚠️  example_output for {model_cls.__name__} did not return a dict or BaseModel"
                )
                return

            output_path = folder / f"{folder_name}_output_example.json"
            output_path.write_text(json.dumps(output_data, indent=2, sort_keys=True))
            print(f"✅ Regenerated output example: {output_path.name}")
        else:
            print(f"⚠️  No example_output method found in {model_cls.__name__}")
    except Exception as e:
        print(
            f"❌ Error generating output example for {folder_name}: {e}",
            file=sys.stderr,
        )


def main():
    args = parse_args()

    if not SCHEMAS_DIR.exists():
        print("❌ schemas/ directory not found", file=sys.stderr)
        sys.exit(1)

    schema_targets = get_schema_targets(args.module)

    for folder_name, folder_path, py_file in schema_targets:
        process_schema_module(folder_name, folder_path, py_file)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--module", help="Only process a specific schema folder", default=None
    )
    return parser.parse_args()


def get_schema_targets(module_filter: str | None):
    schema_targets = find_schema_files()
    if module_filter:
        schema_targets = [t for t in schema_targets if t[0] == module_filter]
        if not schema_targets:
            print(f"❌ No schema folder found named '{module_filter}'", file=sys.stderr)
            sys.exit(1)
    return schema_targets


def process_schema_module(folder_name: str, folder_path: Path, py_file: Path):
    try:
        module = import_model_module(py_file, folder_name)
    except Exception as e:
        print(f"❌ Error importing {py_file}: {e}", file=sys.stderr)
        return

    input_model_cls = None
    output_model_cls = None

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, BaseModel)
            and attr is not BaseModel
        ):
            generate_schema_file(attr, folder_path, folder_name)

            if input_model_cls is None and hasattr(attr, "example_input"):
                input_model_cls = attr
            if output_model_cls is None and hasattr(attr, "example_output"):
                output_model_cls = attr

    if input_model_cls:
        generate_input_example(input_model_cls, folder_path, folder_name)
    if output_model_cls:
        generate_output_example(output_model_cls, folder_path, folder_name)


if __name__ == "__main__":
    main()
