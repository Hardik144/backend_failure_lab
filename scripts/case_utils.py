from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"


def load_case_metadata(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"{path.relative_to(ROOT)}: invalid YAML: {exc}", file=sys.stderr)
        return None

    if not isinstance(data, dict):
        print(f"{path.relative_to(ROOT)}: metadata must be a YAML mapping", file=sys.stderr)
        return None

    return data


def discover_cases() -> dict[str, Path]:
    cases: dict[str, Path] = {}
    for metadata_path in sorted(CASES_DIR.glob("**/case.yaml")):
        data = load_case_metadata(metadata_path)
        if data is None:
            continue
        case_id = data.get("id")
        if isinstance(case_id, str) and case_id:
            cases[case_id] = metadata_path.parent
    return cases
