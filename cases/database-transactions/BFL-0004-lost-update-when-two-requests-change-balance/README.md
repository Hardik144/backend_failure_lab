<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Lost Update When Two Requests Change Balance

## Summary

Two requests withdraw money from the same account at almost the same time. Both read the old balance, then both write a new balance, and one update is lost.

This case teaches the lost update failure: transactions exist, but the code still uses an unsafe read-modify-write pattern.

## Metadata

- ID: `BFL-0004`
- Category: `database-transactions`
- Secondary categories: `reliability-failure-recovery`, `idempotency-consistency`
- Level: `middle`
- Technologies: `python`, `fastapi`, `postgresql`, `sqlalchemy`, `pytest`
- Failure modes: `lost-update`, `race-condition`
- Patterns: `transaction-boundary`, `select-for-update`
- Status: `draft`

## Problem

An account starts with this balance:

```text
balance = 100.00
```

Two requests overlap:

```text
Request A reads balance 100.00
Request B reads balance 100.00
Request A writes balance 70.00
Request B writes balance 80.00
```

The final balance should be `50.00`, but one write overwrites the other and the final balance becomes `80.00`.

## Why This Happens in Production

This bug appears when code reads a row, calculates a new value in application memory, and writes the result back later.

The code can look correct when requests run one at a time. Under concurrent traffic, two transactions can base their updates on the same old value.

Balances, inventory counters, quotas, seats, credits, and usage limits are common places for this bug.

## Broken Scenario

1. Account `#1` has balance `100.00`.
2. Request A withdraws `30.00`.
3. Request B withdraws `20.00`.
4. Both requests read balance `100.00` before either write is visible to the other request.
5. Request A writes `70.00`.
6. Request B writes `80.00`.
7. The `30.00` withdrawal is lost.

## Broken Implementation

The broken implementation performs read-modify-write in application code:

```python
account = get_account(account_id)
account.balance_cents = account.balance_cents - amount_cents
commit()
```

The calculation uses whatever balance was loaded into that session. If another request already changed the row, this code can still write a value based on stale data.

## Where the Bug Happens

The bug happens between the read and the write.

In `broken/repository.py`, `withdraw()` first loads the account object and then assigns a new balance:

```python
account.balance_cents = account.balance_cents - amount_cents
```

That assignment is not an atomic database operation. It is application-side math followed by a later write.

The test makes this explicit by opening two SQLAlchemy sessions. Both sessions read the same initial balance before either writes. Then each session writes its own calculated result.

## How to Catch This Bug

A normal happy-path test is not enough. If the test sends two withdrawals one after another, the broken code may appear correct.

To catch the bug, the test must simulate overlapping work:

1. Open two sessions.
2. Read the same account in both sessions.
3. Calculate two different new balances.
4. Commit both writes.
5. Assert that both withdrawals affected the final balance.

The important assertion is not only that both operations returned success. The final stored balance must include both changes.

## Failing Test

The failing test starts with balance `100.00`.

It simulates two overlapping withdrawals:

- `30.00`
- `20.00`

Safe behavior is final balance `50.00`.

The broken implementation ends with `80.00`, so the test fails.

## Diagnosis

The system fails because the transaction boundary does not protect the business invariant.

The invariant is: every successful withdrawal must reduce the stored balance exactly once.

The broken code does not update the balance relative to the current database value. It updates the balance relative to an old value loaded into memory.

## Fixed Implementation

The fixed implementation uses an atomic database update:

```python
update(Account)
.where(Account.id == account_id)
.values(balance_cents=Account.balance_cents - amount_cents)
```

This tells the database to subtract from the current stored value. The application no longer reads a balance, calculates a new balance, and writes that stale result back. For this case, atomic update is the smallest fix because the operation is a simple counter-style change.

For more complex workflows, PostgreSQL `SELECT FOR UPDATE` can be a better fit: lock the row, read the current value, perform several checks, then write. Optimistic locking is another option when conflicts are rare and the application can retry safely.

## How to Run

From the repository root:

### Broken Version

```bash
make broken CASE=BFL-0004
```

Expected result: this test is expected to fail because one withdrawal is lost.

### Fixed Version

```bash
make fixed CASE=BFL-0004
```

Expected result: the tests should pass because the fixed implementation uses an atomic update.

## Files

- `broken/` - unsafe read-modify-write implementation
- `fixed/` - corrected implementation using atomic update
- `tests/` - tests that simulate overlapping sessions and verify the final balance

## Production Notes

In production, lost updates are often intermittent. They may appear only under traffic spikes or when workers process related jobs at the same time.

For PostgreSQL systems, common fixes are atomic updates, `SELECT FOR UPDATE`, optimistic locking, or carefully designed idempotent commands. The right choice depends on whether the operation is a simple numeric update or a larger workflow with multiple checks.

Always test the invariant you care about. For balances, the final stored value matters more than each individual request returning success.

## Trade-Offs

Atomic update is simple and fast for counter-like changes, but it becomes harder when the business logic needs several reads and validations.

`SELECT FOR UPDATE` is explicit and works well for complex balance logic, but it holds locks and can reduce throughput if transactions are slow.

Optimistic locking avoids long-held locks, but callers must handle conflicts and retries correctly.
