import importlib.util
import json
import sys
from pathlib import Path
from typing import Type

from pydantic import BaseModel

SCHEMAS_DIR = Path("schemas")


def find_schema_files():
    schema_targets = []
    for folder in SCHEMAS_DIR.iterdir():
        if folder.is_dir():
            py_files = list(folder.glob("*.py"))
            if len(py_files) == 1:
                schema_targets.append((folder, py_files[0]))
    return schema_targets


def import_model_module(py_file: Path):
    module_name = f"{py_file.parent.name}.{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {py_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_schema_json(model_cls: Type[BaseModel], output_path: Path):
    try:
        schema_json = model_cls.model_json_schema()
        output_path.write_text(json.dumps(schema_json, indent=2))
    except Exception as e:
        print(
            f"❌ Failed to generate schema for {model_cls.__name__}: {e}",
            file=sys.stderr,
        )


def generate_examples_if_exist(
    model_cls: Type[BaseModel], base_path: Path, prefix: str
):
    try:
        if hasattr(model_cls, "example_input"):
            input_func = model_cls.example_input
            if callable(input_func):
                input_data = input_func()
                (base_path / f"{prefix}_input.example.json").write_text(
                    json.dumps(input_data, indent=2)
                )

        if hasattr(model_cls, "example_output"):
            output_func = model_cls.example_output
            if callable(output_func):
                output_data = output_func()
                (base_path / f"{prefix}_output.example.json").write_text(
                    json.dumps(output_data, indent=2)
                )
    except Exception as e:
        print(
            f"⚠️ Failed to generate examples for {model_cls.__name__}: {e}",
            file=sys.stderr,
        )


def main():
    if not SCHEMAS_DIR.exists():
        print(f"❌ Directory {SCHEMAS_DIR} not found.", file=sys.stderr)
        sys.exit(1)

    schema_folders = find_schema_files()
    if not schema_folders:
        print("No valid schema folders found.")
        return

    for folder, py_file in schema_folders:
        module_name = py_file.stem
        try:
            module = import_model_module(py_file)
        except Exception as e:
            print(f"❌ Error loading module {module_name}: {e}", file=sys.stderr)
            continue

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseModel)
                and attr is not BaseModel
            ):
                model_cls: Type[BaseModel] = attr
                schema_file = folder / f"{module_name}.schema.json"
                generate_schema_json(model_cls, schema_file)
                generate_examples_if_exist(model_cls, folder, module_name)
                print(f"✅ Generated: {folder.name}/{attr_name}")


if __name__ == "__main__":
    main()
