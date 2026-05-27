# Contributing

Backend Failure Lab is built around small, practical backend failure cases.

## Add a New Case

1. Copy `templates/case-template/` into the matching directory under `cases/`.
2. Rename the copied directory to a clear case slug.
3. Fill in `case.yaml`.
4. Add the broken implementation under `broken/`.
5. Add the fixed implementation under `fixed/`.
6. Add tests under `tests/`.
7. Update the catalog files or run `python scripts/generate_catalog.py`.

## Case Expectations

- Keep each case focused on one failure mode.
- Include a failing test that proves the broken behavior.
- Explain the diagnosis and production impact.
- Use tags from [TAGS.md](TAGS.md).
- Do not add unrelated architecture or infrastructure.

## Running Cases

Each case must include:

- a `case.yaml` file with a unique `id`;
- `tests/test_broken.py`;
- `tests/test_fixed.py`.

Run cases through Docker from the repository root:

```bash
make broken CASE=<case-id>
make fixed CASE=<case-id>
```

Before opening a pull request, run:

```bash
make test
make validate-cases
```
