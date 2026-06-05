from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_main_directories_exist() -> None:
    for path in [
        "cases",
        "catalog",
        "templates/case-template",
        "scripts",
        "tests",
    ]:
        assert (ROOT / path).is_dir()


def test_case_template_metadata_exists() -> None:
    assert (ROOT / "templates/case-template/case.yaml").is_file()


def test_catalog_files_exist() -> None:
    for path in [
        "catalog/README.md",
        "catalog/by-category.md",
        "catalog/by-technology.md",
        "catalog/by-level.md",
    ]:
        assert (ROOT / path).is_file()


def test_main_docs_exist() -> None:
    for path in [
        "README.md",
        "ROADMAP.md",
        "CASE_FORMAT.md",
        "TAGS.md",
        "CONTRIBUTING.md",
        "LICENSE",
    ]:
        assert (ROOT / path).is_file()



def test_case_runner_exists() -> None:
    assert (ROOT / "scripts/run_case.py").is_file()


def test_makefile_has_generic_case_targets() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "broken:" in makefile
    assert "fixed:" in makefile
    assert "scripts/run_case.py" in makefile


def test_case_template_has_id_field() -> None:
    template = (ROOT / "templates/case-template/case.yaml").read_text(encoding="utf-8")

    assert "id:" in template


def test_case_utils_exists() -> None:
    assert (ROOT / "scripts/case_utils.py").is_file(), (
        "scripts/case_utils.py does not exist. "
        "Create it with discover_cases() and load_case_metadata()."
    )


def test_run_case_uses_case_utils() -> None:
    run_case = (ROOT / "scripts/run_case.py").read_text(encoding="utf-8")
    assert "from case_utils import" in run_case, (
        "run_case.py must import from case_utils, not define functions inline."
    )
    assert "def load_case_metadata" not in run_case, (
        "load_case_metadata() must be moved to case_utils.py."
    )
    assert "def discover_cases" not in run_case, (
        "discover_cases() must be moved to case_utils.py."
    )


def test_no_comment_only_database_py_in_cases() -> None:
    offenders = []
    for db_file in sorted((ROOT / "cases").rglob("database.py")):
        if "__pycache__" in str(db_file):
            continue
        content = db_file.read_text(encoding="utf-8").strip()
        non_comment = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        if not non_comment:
            offenders.append(str(db_file.relative_to(ROOT)))
    assert not offenders, (
        f"database.py files contain only comments (no real code): {offenders}. "
        "Delete them if unused, or add real content."
    )


def test_no_test_fixed_py_in_cases() -> None:
    leftover = sorted((ROOT / "cases").rglob("test_fixed.py"))
    assert not leftover, (
        f"test_fixed.py still exists in {len(leftover)} case(s): "
        f"{[str(p.relative_to(ROOT)) for p in leftover]}. "
        "Rename to test_behavior.py and add conftest.py."
    )


def test_all_cases_have_test_behavior_py() -> None:
    missing = []
    for tests_dir in sorted((ROOT / "cases").rglob("tests")):
        if tests_dir.is_dir() and (tests_dir / "test_broken.py").is_file():
            if not (tests_dir / "test_behavior.py").is_file():
                missing.append(str(tests_dir.relative_to(ROOT)))
    assert not missing, f"test_behavior.py missing in: {missing}"


def test_all_cases_have_conftest() -> None:
    missing = []
    for tests_dir in sorted((ROOT / "cases").rglob("tests")):
        if tests_dir.is_dir() and (tests_dir / "test_broken.py").is_file():
            if not (tests_dir / "conftest.py").is_file():
                missing.append(str(tests_dir.relative_to(ROOT)))
    assert not missing, f"conftest.py missing in: {missing}"


def test_claude_md_lists_all_cases() -> None:
    import yaml

    cases_root = ROOT / "cases"
    case_yamls = sorted(cases_root.rglob("case.yaml"))

    expected = {}
    for path in case_yamls:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        expected[data["id"]] = data["status"]

    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    missing_ids = [id_ for id_ in expected if id_ not in claude_md]
    assert not missing_ids, (
        f"CLAUDE.md is missing case IDs: {missing_ids}. "
        "Update the 'Current State' section to include all cases."
    )


def test_ci_workflow_exists() -> None:
    assert (ROOT / ".github/workflows/ci.yml").is_file(), (
        ".github/workflows/ci.yml does not exist. "
        "Create it with validate and lint jobs (no Docker)."
    )


def test_validate_metadata_checks_valid_statuses() -> None:
    script = (ROOT / "scripts/validate_case_metadata.py").read_text(encoding="utf-8")
    assert "VALID_STATUSES" in script, (
        "validate_case_metadata.py must define VALID_STATUSES. "
        "Add: VALID_STATUSES = {\"released\", \"draft\", \"archived\"}"
    )


def test_validate_metadata_checks_released_structure() -> None:
    script = (ROOT / "scripts/validate_case_metadata.py").read_text(encoding="utf-8")
    assert "RELEASED_REQUIRED_DIRS" in script, (
        "validate_case_metadata.py must define RELEASED_REQUIRED_DIRS. "
        "Add directory structure validation for released cases."
    )
    assert "RELEASED_REQUIRED_FILES" in script, (
        "validate_case_metadata.py must define RELEASED_REQUIRED_FILES. "
        "Add file structure validation for released cases."
    )


def test_pyproject_has_asyncio_mode() -> None:
    import tomllib

    with open(ROOT / "pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    pytest_opts = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "asyncio_mode" in pytest_opts, (
        "asyncio_mode is missing from [tool.pytest.ini_options] in pyproject.toml. "
        "Add asyncio_mode = 'auto' to avoid unpredictable behavior across pytest-asyncio versions."
    )
