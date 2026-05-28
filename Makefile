.PHONY: install test lint validate-cases generate-catalog up down check-docker check-case docker-shell docker-test broken fixed docker-bfl-0001-broken docker-bfl-0001-fixed

install:
	python -m pip install -e ".[dev]"

test: check-docker
	docker compose run --rm --build lab pytest tests 

lint: check-docker
	docker compose run --rm --build lab ruff check .

validate-cases: check-docker
	docker compose run --rm --build lab python scripts/validate_case_metadata.py

generate-catalog: check-docker
	docker compose run --rm --build lab python scripts/generate_catalog.py

up:
	docker compose up -d

down:
	docker compose down

check-docker:
	@docker info > /dev/null 2>&1 || (echo "Docker is not running. Start Docker Desktop and try again." && exit 1)

check-case:
	@if [ -z "$(CASE)" ]; then \
		echo "Please provide CASE, example: make broken CASE=BFL-0001"; \
		exit 1; \
	fi

docker-shell: check-docker
	docker compose run --rm --build lab bash

docker-test: check-docker
	docker compose run --rm --build lab pytest tests

broken: check-case check-docker
	@docker compose run --rm --build lab sh -c 'python scripts/run_case.py --case $(CASE) --mode broken; status=$$?; if [ $$status -eq 1 ]; then exit 42; else exit $$status; fi'; \
	status=$$?; \
	if [ $$status -eq 42 ]; then \
		echo ""; \
		echo "Expected failure: the broken implementation demonstrates the bug."; \
		exit 0; \
	else \
		exit $$status; \
	fi

fixed: check-case check-docker
	docker compose run --rm --build lab python scripts/run_case.py --case $(CASE) --mode fixed

docker-bfl-0001-broken:
	$(MAKE) broken CASE=BFL-0001

docker-bfl-0001-fixed:
	$(MAKE) fixed CASE=BFL-0001
