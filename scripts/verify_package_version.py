"""Verify that a built wheel has the expected module version."""

import argparse
import ast
import sys
import zipfile
from email.parser import BytesParser
from pathlib import Path


def get_module_version(module_path: Path) -> str:
    module = ast.parse(module_path.read_text(encoding="utf-8"))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__version__"
            for target in statement.targets
        ):
            continue
        if isinstance(statement.value, ast.Constant) and isinstance(
            statement.value.value, str
        ):
            return statement.value.value
        raise ValueError("__version__ must be a string literal")
    raise ValueError("__version__ is not defined")


def get_wheel_version(wheel_path: Path) -> str:
    with zipfile.ZipFile(wheel_path) as wheel:
        metadata_path = next(
            path
            for path in wheel.namelist()
            if path.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))
    version = metadata["Version"]
    if version is None:
        raise ValueError("wheel metadata does not define a version")
    return version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--expected")
    args = parser.parse_args()

    module_version = get_module_version(Path("beanie/__init__.py"))
    wheel_version = get_wheel_version(args.wheel)
    expected_version = args.expected or module_version

    if module_version != expected_version or wheel_version != expected_version:
        raise ValueError(
            "Version mismatch: "
            f"module={module_version}, wheel={wheel_version}, "
            f"expected={expected_version}"
        )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
