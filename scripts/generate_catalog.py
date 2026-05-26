from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
CATALOG_DIR = ROOT / "catalog"

CATEGORIES = [
    "api-http",
    "database-transactions",
    "queues-background-jobs",
    "reliability-failure-recovery",
    "idempotency-consistency",
    "caching-redis",
    "security-auth",
    "observability-debugging",
    "performance-scaling",
    "deployment-operations",
]

TECHNOLOGIES = [
    "python",
    "fastapi",
    "postgresql",
    "sqlalchemy",
    "alembic",
    "redis",
    "celery",
    "dramatiq",
    "pytest",
    "docker-compose",
]

LEVELS = [
    "beginner",
    "junior",
    "junior-middle",
    "middle",
    "middle-advanced",
    "advanced",
]


def read_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(CASES_DIR.glob("**/case.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        data["_path"] = path.parent.relative_to(ROOT).as_posix()
        cases.append(data)
    return cases


def case_line(case: dict[str, Any]) -> str:
    title = case.get("title") or case.get("slug") or case.get("id") or "Untitled case"
    path = case.get("_path", "")
    return f"- [{title}](../{path}/)"


def render_grouped(title: str, keys: list[str], grouped: dict[str, list[dict[str, Any]]]) -> str:
    lines = [f"# {title}", ""]
    for key in keys:
        lines.extend([f"## {key}", ""])
        items = grouped.get(key, [])
        if items:
            lines.extend(case_line(item) for item in items)
        else:
            lines.append("No cases yet.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    cases = read_cases()

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_technology: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for case in cases:
        primary_category = case.get("primary_category")
        if isinstance(primary_category, str):
            by_category[primary_category].append(case)

        for technology in case.get("technologies", []):
            if isinstance(technology, str):
                by_technology[technology].append(case)

        level = case.get("level")
        if isinstance(level, str):
            by_level[level].append(case)

    (CATALOG_DIR / "by-category.md").write_text(
        render_grouped("Cases by Category", CATEGORIES, by_category),
        encoding="utf-8",
    )
    (CATALOG_DIR / "by-technology.md").write_text(
        render_grouped("Cases by Technology", TECHNOLOGIES, by_technology),
        encoding="utf-8",
    )
    (CATALOG_DIR / "by-level.md").write_text(
        render_grouped("Cases by Level", LEVELS, by_level),
        encoding="utf-8",
    )

    print(f"Generated catalog files for {len(cases)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
