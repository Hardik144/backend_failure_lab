from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
VALID_MODES = {"broken", "fixed"}


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Backend Failure Lab case tests.")
    parser.add_argument("--case", dest="case_id", help="Case ID from case.yaml, for example BFL-0001")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), help="Test mode to run")
    args = parser.parse_args()

    if not args.case_id:
        parser.error("Please provide --case, example: --case BFL-0001")
    if not args.mode:
        parser.error("Please provide --mode, either broken or fixed")

    return args


def main() -> int:
    args = parse_args()
    cases = discover_cases()

    case_dir = cases.get(args.case_id)
    if case_dir is None:
        available = ", ".join(sorted(cases)) or "none"
        print(f"Case not found: {args.case_id}", file=sys.stderr)
        print(f"Available case IDs: {available}", file=sys.stderr)
        return 2

    test_path = case_dir / "tests" / f"test_{args.mode}.py"
    if not test_path.is_file():
        print(
            f"Missing test file for {args.case_id} {args.mode}: "
            f"{test_path.relative_to(ROOT)}",
            file=sys.stderr,
        )
        return 2

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
