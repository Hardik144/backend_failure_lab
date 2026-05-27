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
