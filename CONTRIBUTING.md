# Contributing

Backend Failure Lab is built around small, practical backend failure cases.

## Add a New Case

1. Choose the next global `BFL` ID.
2. Choose the primary category.
3. Create the case folder:

```text
cases/<primary-category>/BFL-XXXX-short-slug/
```

4. Fill in `case.yaml`.
5. Add `README.md`, `README.ru.md`, `broken/`, `fixed/`, `tests/`, and `assets/` when needed.
6. Add the case to the visible catalog:
   - root `README.md` -> `Browse by Category`;
   - root `README.md` -> `Featured Cases`, if the case is important for the current release;
   - `catalog/` files, if they are currently maintained manually.
7. Run the case:

```bash
make broken CASE=BFL-XXXX
make fixed CASE=BFL-XXXX
```

Do not invent category-specific IDs such as `SA-0001`, `PS-0001`, or `DB-0001`. Categories belong in `case.yaml`; IDs must stay global and stable.

## Case Expectations

- Keep each case focused on one failure mode.
- Include a failing test that proves the broken behavior.
- Explain the diagnosis and production impact.
- Use tags from [TAGS.md](TAGS.md).
- Do not add unrelated architecture or infrastructure.

## Running Cases

Each case must include:

- a `case.yaml` file with a unique global `BFL-XXXX` ID;
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
