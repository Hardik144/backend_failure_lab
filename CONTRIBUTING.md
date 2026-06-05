# Contributing

Backend Failure Lab is built around small, practical backend failure cases.

## You Can Contribute Without Writing Code

Backend Failure Lab accepts real backend failure stories, not only code contributions.

You can open a **Failure Case Proposal** issue if you have seen a bug or failure pattern that could become a reproducible case.

A good proposal should include:

- what breaks;
- where this happens in production;
- step-by-step broken scenario;
- expected safe behavior;
- possible fix or pattern, if known;
- similar existing cases, if any.

You do not need to implement the case yourself.

## Failure Case Proposal Flow

1. Contributor opens a Failure Case Proposal issue.
2. Maintainer reviews it.
3. If it is useful and not a duplicate, maintainer adds `accepted-case`.
4. If it is too similar to an existing case, maintainer adds `duplicate` or `extension`.
5. If accepted, it can later become a full case implementation task.
6. Small tasks can be split into `good first issue` issues.

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
- `tests/test_broken.py` — proves the bug exists, must fail on `broken/`;
- `tests/test_behavior.py` — proves safe behavior, must pass on `fixed/`;
- `tests/conftest.py` — wires up the `BFL_IMPL` path injection (copy from `templates/case-template/tests/`).

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
