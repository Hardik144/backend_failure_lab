# Backend Failure Lab

Learn backend engineering through real production failure cases.

Backend Failure Lab is a practical training repository for Python backend developers. Each future case will follow the same flow:

`broken code -> failing test -> diagnosis -> fix -> production notes`

The project is currently in MVP stage. This repository contains the initial structure, case template, catalog placeholders, and validation scripts. Real cases will be added later.

## How It Works

Each case is a small, focused backend failure scenario. A case starts with a broken implementation and a failing test, then walks through the diagnosis, the corrected implementation, and notes about how the same issue appears in production systems.

Cases are meant to be practical, reproducible, and easy to review in pull requests.

## Browse Cases

- [Catalog overview](catalog/README.md)
- [By category](catalog/by-category.md)
- [By technology](catalog/by-technology.md)
- [By level](catalog/by-level.md)

## Case Categories

- API and HTTP behavior
- Database transactions
- Queues and background jobs
- Reliability, failure, and recovery
- Idempotency and consistency
- Redis caching
- Security and authorization
- Observability and debugging
- Performance and scaling
- Deployment and operations

## Current Status

- Repository scaffold: ready
- Case template: ready
- Catalog structure: ready
- Real cases: not added yet

## Contributing

Contributions will focus on small, production-inspired backend failure cases. Start with the [case format](CASE_FORMAT.md), use the [case template](templates/case-template/), and keep each case narrow enough to explain through one failing test.
