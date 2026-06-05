from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"

REQUIRED_FIELDS = {
    "id",
    "title",
    "slug",
    "primary_category",
    "level",
    "technologies",
    "failure_modes",
    "patterns",
    "status",
    "created_at",
    "updated_at",
}

VALID_STATUSES = {"released", "draft", "archived"}

RELEASED_REQUIRED_DIRS = ["broken", "fixed", "tests"]
RELEASED_REQUIRED_FILES = [
    "tests/test_broken.py",
    "tests/test_behavior.py",
]


def load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"{path}: invalid YAML: {exc}")
        return None

    if not isinstance(data, dict):
        print(f"{path}: metadata must be a YAML mapping")
        return None

    return data


def validate_file(path: Path) -> list[str]:
    data = load_yaml(path)
    if data is None:
        return ["invalid metadata file"]

    case_dir = path.parent
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    for field in ("technologies", "failure_modes", "patterns"):
        if field in data and not isinstance(data[field], list):
            errors.append(f"{field} must be a list")

    status = data.get("status")
    if status is not None and status not in VALID_STATUSES:
        errors.append(
            f"status must be one of {sorted(VALID_STATUSES)}, got: {status!r}"
        )

    if status == "released":
        for dirname in RELEASED_REQUIRED_DIRS:
            if not (case_dir / dirname).is_dir():
                errors.append(f"released case missing directory: {dirname}/")
        for filename in RELEASED_REQUIRED_FILES:
            if not (case_dir / filename).is_file():
                errors.append(f"released case missing file: {filename}")

    return errors


def main() -> int:
    case_files = sorted(CASES_DIR.glob("**/case.yaml"))
    if not case_files:
        print("No case.yaml files found under cases/.")
        return 0

    failed = False
    for path in case_files:
        errors = validate_file(path)
        if errors:
            failed = True
            for error in errors:
                print(f"{path.relative_to(ROOT)}: {error}")
        else:
            print(f"{path.relative_to(ROOT)}: ok")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
