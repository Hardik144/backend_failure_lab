from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

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

CATEGORY_DISPLAY: dict[str, str] = {
    "api-http": "API & HTTP",
    "database-transactions": "Database & Transactions",
    "queues-background-jobs": "Queues & Background Jobs",
    "reliability-failure-recovery": "Reliability & Failure Recovery",
    "idempotency-consistency": "Idempotency & Consistency",
    "caching-redis": "Caching & Redis",
    "security-auth": "Security & Auth",
    "observability-debugging": "Observability & Debugging",
    "performance-scaling": "Performance & Scaling",
    "deployment-operations": "Deployment & Operations",
}


def _display_level(level: str) -> str:
    return "-".join(word.capitalize() for word in level.split("-"))


def _display_status(status: str) -> str:
    return status.capitalize()


def _display_category(category: str) -> str:
    return CATEGORY_DISPLAY.get(category, category)


def read_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(CASES_DIR.glob("**/case.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        data["_path"] = path.parent.relative_to(ROOT).as_posix()
        cases.append(data)
    return cases


def _case_header(n: int, case: dict[str, Any]) -> str:
    case_id = case.get("id", "")
    title = case.get("title") or case.get("slug") or case_id or "Untitled case"
    path = case.get("_path", "")
    return f"{n}. **{case_id}** — [{title}](../{path})  "


def _case_line_category(n: int, case: dict[str, Any]) -> str:
    level = _display_level(case.get("level", ""))
    status = _display_status(case.get("status", ""))
    return f"{_case_header(n, case)}\n   Level: {level} · Status: {status}"


def _case_line_level(n: int, case: dict[str, Any]) -> str:
    category = _display_category(case.get("primary_category", ""))
    status = _display_status(case.get("status", ""))
    return f"{_case_header(n, case)}\n   Category: {category} · Status: {status}"


def _case_line_technology(n: int, case: dict[str, Any]) -> str:
    category = _display_category(case.get("primary_category", ""))
    level = _display_level(case.get("level", ""))
    status = _display_status(case.get("status", ""))
    return f"{_case_header(n, case)}\n   Category: {category} · Level: {level} · Status: {status}"


def render_grouped(
    title: str,
    keys: list[str],
    grouped: dict[str, list[dict[str, Any]]],
    line_fn: Callable[[int, dict[str, Any]], str],
) -> str:
    lines = [f"# {title}", ""]
    for key in keys:
        lines.extend([f"## {key}", ""])
        items = grouped.get(key, [])
        if items:
            for n, item in enumerate(items, start=1):
                lines.append(line_fn(n, item))
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
        for secondary_category in case.get("secondary_categories", []):
            if isinstance(secondary_category, str):
                by_category[secondary_category].append(case)

        for technology in case.get("technologies", []):
            if isinstance(technology, str):
                by_technology[technology].append(case)

        level = case.get("level")
        if isinstance(level, str):
            by_level[level].append(case)

    for group in (by_category, by_technology, by_level):
        for key in group:
            group[key].sort(key=lambda c: c.get("id", ""))

    (CATALOG_DIR / "by-category.md").write_text(
        render_grouped("Cases by Category", CATEGORIES, by_category, _case_line_category),
        encoding="utf-8",
    )
    (CATALOG_DIR / "by-technology.md").write_text(
        render_grouped("Cases by Technology", TECHNOLOGIES, by_technology, _case_line_technology),
        encoding="utf-8",
    )
    (CATALOG_DIR / "by-level.md").write_text(
        render_grouped("Cases by Level", LEVELS, by_level, _case_line_level),
        encoding="utf-8",
    )

    print(f"Generated catalog files for {len(cases)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
