<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Background Job Commits Too Early Before External Call

A background-style operation marks an order as confirmed before the external notification succeeds.

This case teaches a partial failure: local database state says the work is done, but the external side effect failed.

## Metadata

- ID: `BFL-0009`
- Category: `queues-background-jobs`
- Secondary categories: `reliability-failure-recovery`, `database-transactions`
- Level: `middle`
- Technologies: `python`, `fastapi`, `postgresql`, `sqlalchemy`, `pytest`
- Failure modes: `partial-failure`
- Patterns: `outbox-pattern`, `transaction-boundary`
- Status: `draft`

## Problem

The API confirms an order and then sends an external confirmation notification. The broken implementation commits `order.status = "confirmed"` before the notification call finishes.

If the external call fails, the user sees an error, but the database already says the order is confirmed.

## Why This Happens in Production

This happens when code treats a multi-step workflow as if every step succeeds together. A database commit is durable, but a later HTTP call, email, payment request, or webhook can still fail.

The dangerous part is that retrying the job later now starts from misleading state. The system may skip work because it believes the order is already confirmed.

## Broken Scenario

1. Order `100` is pending.
2. The backend starts confirmation.
3. The backend commits `status = confirmed`.
4. The notification service fails.
5. The endpoint returns `503`.
6. The order still stays confirmed in the database.

## Broken Implementation

The broken code commits local state too early:

```python
order.status = "confirmed"
session.commit()
send_confirmation_notification()
```

## Where Exactly It Breaks

The bug is in `broken/repository.py`, inside `confirm_order`. The function crosses a boundary between database state and an external side effect, but it commits before the external side effect is known to be safe.

That means the database no longer represents what actually happened.

## How To Catch It

Test the failure path, not only the happy path. Force the external notification to fail and then read the order from the database.

The important assertion is not only the HTTP status. The important assertion is that failed external work must not leave final successful state behind.

## Failing Test

`tests/test_broken.py` expects the order to stay pending when the external notification fails.

The broken implementation returns `503`, but the stored order becomes `confirmed`, so the test fails.

## Diagnosis

Authentication, validation, and database writes can all be correct in isolation while the workflow is still unsafe.

The backend needs a clear transaction boundary around local state and a safe strategy for external side effects. In a larger system, this is often handled with an outbox table: write the intended external event durably, then let a retryable worker deliver it.

## Fixed Implementation

The fixed implementation does not commit final success before the notification succeeds:

```python
send_confirmation_notification()
order.status = "confirmed"
order.confirmation_sent = True
session.commit()
```

For this small lab case, that keeps final state honest. In production, the stronger version is usually an outbox pattern, because external calls cannot be part of the same database transaction.

## How to Run

From the repository root:

### Broken version

```bash
make broken CASE=BFL-0009
```

Expected: the test should fail because the broken implementation leaves the order confirmed after a failed external call.

### Fixed version

```bash
make fixed CASE=BFL-0009
```

Expected: the tests should pass because the fixed implementation does not commit final success before the external side effect succeeds.

## Files

- `broken/` — intentionally unsafe implementation
- `fixed/` — corrected implementation
- `tests/` — tests that demonstrate the failure and verify the fix

## Production Notes

- Do not mark work as complete before all required local invariants are true.
- Treat external calls as unreliable even when they usually work.
- Prefer retryable workflow states such as `pending`, `processing`, and `confirmed`.
- For durable external side effects, consider an outbox pattern.

## Trade-Offs

Calling the external service before committing final state is simple, but it still cannot make the external service atomic with the database.

An outbox is safer for production workflows, but it adds another table, a dispatcher, retries, and monitoring. For small code, explicit state transitions may be enough.
