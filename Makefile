.PHONY: install test lint validate-cases generate-catalog up down

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .

validate-cases:
	python scripts/validate_case_metadata.py

generate-catalog:
	python scripts/generate_catalog.py

up:
	docker compose up -d

down:
	docker compose down
