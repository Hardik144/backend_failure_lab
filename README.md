# Backend Failure Lab

Learn backend engineering through real production failure cases.

Backend Failure Lab is a practical training repository for Python backend developers. Each case follows the same flow:

`broken code -> failing test -> diagnosis -> fix -> production notes`

The project is currently in MVP stage. Runnable cases are available, and more cases will be added over time.

## How It Works

Each case is a small, focused backend failure scenario. A case starts with a broken implementation and a failing test, then walks through the diagnosis, the corrected implementation, and notes about how the same issue appears in production systems.

Cases are meant to be practical, reproducible, and easy to review in pull requests.

## Run a Case

The recommended way is Docker. You do not need to install Python dependencies locally.

`CASE` is the case ID from `case.yaml`.

Broken version:

```bash
make broken CASE=BFL-0001
```

Expected result: the broken test is expected to fail because it demonstrates the bug.

Fixed version:

```bash
make fixed CASE=BFL-0001
```

Expected result: the fixed test should pass.

## Suggest a Failure Case

You do not need to write code to contribute.

If you have seen a real backend failure in practice, you can suggest it as a future case:

- auth bugs
- N+1 queries
- unsafe retries
- stale cache
- race conditions
- transaction bugs
- background job failures
- missing request IDs
- observability/debugging problems

Open a **Failure Case Proposal** issue and describe the scenario.

A maintainer can later turn it into:

`broken code -> failing test -> diagnosis -> fix -> production notes`

## Ways to Contribute

You can help by:

1. Suggesting a real backend failure case.
2. Improving an existing case explanation.
3. Adding tests.
4. Implementing broken/fixed examples.
5. Adding diagrams.
6. Reviewing whether a case feels realistic.

## Browse by Category

<details>
<summary><strong>API & HTTP</strong></summary>

1. **BFL-0001** — [User Can Read Another User's Order](cases/security-auth/BFL-0001-user-can-read-another-users-order)  
   Level: Beginner · Status: Released
2. **BFL-0005** — [Missing Request ID Makes Debugging Impossible](cases/observability-debugging/BFL-0005-missing-request-id-makes-debugging-impossible)  
   Level: Beginner · Status: Draft
3. **BFL-0007** — [Blocking Code Inside Async Endpoint](cases/performance-scaling/BFL-0007-blocking-code-inside-async-endpoint)  
   Level: Junior · Status: Draft
4. **BFL-0008** — [Offset Pagination Skips or Duplicates Items](cases/api-http/BFL-0008-offset-pagination-skips-or-duplicates-items)  
   Level: Junior · Status: Draft

</details>

<details>
<summary><strong>Database & Transactions</strong></summary>

1. **BFL-0002** — [N+1 Queries Hidden Behind a Simple Endpoint](cases/database-transactions/BFL-0002-n-plus-one-queries-hidden-behind-simple-endpoint)  
   Level: Junior · Status: Draft
2. **BFL-0004** — [Lost Update When Two Requests Change Balance](cases/database-transactions/BFL-0004-lost-update-when-two-requests-change-balance)  
   Level: Middle · Status: Draft
3. **BFL-0008** — [Offset Pagination Skips or Duplicates Items](cases/api-http/BFL-0008-offset-pagination-skips-or-duplicates-items)  
   Level: Junior · Status: Draft

</details>

<details>
<summary><strong>Queues & Background Jobs</strong></summary>

1. **BFL-0003** — [Retry Without Idempotency Creates Duplicate Orders](cases/idempotency-consistency/BFL-0003-retry-without-idempotency-creates-duplicate-orders)  
   Level: Junior-Middle · Status: Draft

</details>

<details>
<summary><strong>Reliability & Failure Recovery</strong></summary>

1. **BFL-0004** — [Lost Update When Two Requests Change Balance](cases/database-transactions/BFL-0004-lost-update-when-two-requests-change-balance)  
   Level: Middle · Status: Draft
2. **BFL-0005** — [Missing Request ID Makes Debugging Impossible](cases/observability-debugging/BFL-0005-missing-request-id-makes-debugging-impossible)  
   Level: Beginner · Status: Draft

</details>

<details>
<summary><strong>Idempotency & Consistency</strong></summary>

1. **BFL-0003** — [Retry Without Idempotency Creates Duplicate Orders](cases/idempotency-consistency/BFL-0003-retry-without-idempotency-creates-duplicate-orders)  
   Level: Junior-Middle · Status: Draft
2. **BFL-0004** — [Lost Update When Two Requests Change Balance](cases/database-transactions/BFL-0004-lost-update-when-two-requests-change-balance)  
   Level: Middle · Status: Draft
3. **BFL-0006** — [Cache Returns Stale User Profile After Update](cases/caching-redis/BFL-0006-cache-returns-stale-user-profile-after-update)  
   Level: Junior · Status: Draft

</details>

<details>
<summary><strong>Caching & Redis</strong></summary>

1. **BFL-0006** — [Cache Returns Stale User Profile After Update](cases/caching-redis/BFL-0006-cache-returns-stale-user-profile-after-update)  
   Level: Junior · Status: Draft

</details>

<details>
<summary><strong>Security & Auth</strong></summary>

1. **BFL-0001** — [User Can Read Another User's Order](cases/security-auth/BFL-0001-user-can-read-another-users-order)  
   Level: Beginner · Status: Released

</details>

<details>
<summary><strong>Observability & Debugging</strong></summary>

1. **BFL-0005** — [Missing Request ID Makes Debugging Impossible](cases/observability-debugging/BFL-0005-missing-request-id-makes-debugging-impossible)  
   Level: Beginner · Status: Draft

</details>

<details>
<summary><strong>Performance & Scaling</strong></summary>

1. **BFL-0002** — [N+1 Queries Hidden Behind a Simple Endpoint](cases/database-transactions/BFL-0002-n-plus-one-queries-hidden-behind-simple-endpoint)  
   Level: Junior · Status: Draft
2. **BFL-0007** — [Blocking Code Inside Async Endpoint](cases/performance-scaling/BFL-0007-blocking-code-inside-async-endpoint)  
   Level: Junior · Status: Draft
3. **BFL-0008** — [Offset Pagination Skips or Duplicates Items](cases/api-http/BFL-0008-offset-pagination-skips-or-duplicates-items)  
   Level: Junior · Status: Draft

</details>

<details>
<summary><strong>Deployment & Operations</strong></summary>

No cases yet.

</details>

## Case ID Convention

`BFL` means `Backend Failure Lab`.

Case IDs are global, stable, and independent from categories. Categories belong in `case.yaml`, not in the ID.

Use the primary category only for the folder path:

```text
cases/security-auth/BFL-0001-user-can-read-another-users-order/
```

## Catalog Files

- [Catalog overview](catalog/README.md)
- [By category](catalog/by-category.md)
- [By technology](catalog/by-technology.md)
- [By level](catalog/by-level.md)

## Current Status

- Repository scaffold: ready
- Docker-based case runner: ready
- Runnable cases: 8
- Case template: ready
- Catalog structure: ready

## Contributing

Contributions should focus on small, production-inspired backend failure cases. Start with the [case format](CASE_FORMAT.md), use the [case template](templates/case-template/), and keep each case narrow enough to explain through one failing test.
