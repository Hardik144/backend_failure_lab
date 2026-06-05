from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from case_utils import discover_cases


ROOT = Path(__file__).resolve().parents[1]
VALID_MODES = {"broken", "fixed"}


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

    test_filename = "test_behavior.py" if args.mode == "fixed" else f"test_{args.mode}.py"
    test_path = case_dir / "tests" / test_filename
    if not test_path.is_file():
        print(
            f"Missing test file for {args.case_id} {args.mode}: "
            f"{test_path.relative_to(ROOT)}",
            file=sys.stderr,
        )
        return 2

    env = {**os.environ, "BFL_IMPL": args.mode}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path.relative_to(ROOT))],
        cwd=ROOT,
        env=env,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
