<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Retry Without Idempotency Creates Duplicate Orders

## Summary

A user creates an order, the same operation is retried, and the backend creates a second order.

The bug is not in the JSON response or validation. The bug is that the backend treats a retry as a brand-new command.

## Metadata

- ID: `BFL-0003`
- Category: `idempotency-consistency`
- Secondary category: `queues-background-jobs`
- Level: `junior-middle`
- Technologies: `python`, `fastapi`, `postgresql`, `sqlalchemy`, `pytest`
- Failure modes: `duplicate-processing`
- Patterns: `idempotency-key`
- Status: `draft`

## Problem

The API exposes an endpoint:

```http
POST /orders
```

A client sends the request with an `Idempotency-Key` header. If the client retries the same operation with the same key, the backend should return the same order instead of creating a duplicate.

The broken implementation accepts the key but does not use it to detect retries.

## Why This Happens in Production

Retries are normal in production systems. They can come from HTTP clients, load balancers, webhook senders, background jobs, or workers after a timeout.

Without idempotency, a retry can repeat a side effect. For orders and payments, this can mean duplicate orders, duplicate charges, duplicate emails, or duplicate background jobs.

## Broken Scenario

1. The client sends `POST /orders` with `Idempotency-Key: same-command`.
2. The backend creates order `#1`.
3. The client retries the same request with the same key.
4. The backend creates order `#2`.
5. One user action produced two orders.

## Broken Implementation

The broken endpoint validates that `Idempotency-Key` exists, then creates a new order every time:

```python
order = create_order(payload=payload, idempotency_key=idempotency_key)
```

In `broken/repository.py`, `create_order()` always inserts a new row. The idempotency key is stored, but it is never used to look up an existing order.

## Where the Bug Happens

The bug happens before the database insert.

The backend has enough information to detect a retry because the request includes `Idempotency-Key`. The missing step is checking whether an order with that key already exists before inserting a new row.

The risky pattern is:

```python
receive command
insert row
return row
```

The safer pattern is:

```python
receive command
find existing row by idempotency key
if found: return existing row
else: insert row
```

## How to Catch This Bug

Use a test that sends the same command twice.

Do not only assert that both responses are successful. Also assert that the second response returns the same order and that the database contains only one order.

This catches the real production failure: repeated execution changes state twice.

## Failing Test

The failing test sends two identical `POST /orders` requests with the same `Idempotency-Key`.

Safe behavior is:

- both responses refer to the same order;
- the database contains exactly one order.

The broken implementation creates two orders, so the test fails.

## Diagnosis

The system fails because command identity is not stored as part of the write path.

The backend sees two HTTP requests and treats them as two independent create commands. The `Idempotency-Key` should identify the operation, not just decorate the request.

## Fixed Implementation

The fixed implementation checks the idempotency key before creating a new order:

```python
existing_order = get_order_by_idempotency_key(idempotency_key)
if existing_order is not None:
    return existing_order
```

Only the first request creates a row. A retry with the same key returns the existing row, so the operation becomes safe to repeat. In real production systems, this should also be protected by a database uniqueness constraint on the idempotency key to handle concurrent retries.

## How to Run

From the repository root:

### Broken Version

```bash
make broken CASE=BFL-0003
```

Expected result: this test is expected to fail because the broken implementation creates duplicate orders.

### Fixed Version

```bash
make fixed CASE=BFL-0003
```

Expected result: the tests should pass because the fixed implementation returns the existing order for a repeated key.

## Files

- `broken/` - implementation that ignores the idempotency key during writes
- `fixed/` - implementation that checks the idempotency key before inserting
- `tests/` - tests that verify repeated commands do not create duplicate orders

## Production Notes

This case uses a simple HTTP retry to keep the first version small. The same failure appears with queues, webhooks, workers, and payment flows.

A future case can add Redis, Celery, or a real worker retry loop. The core principle stays the same: repeated execution of the same command must not repeat the side effect.

For production, idempotency should usually be enforced with a durable store and a unique constraint. Application-level checks are useful, but the database should protect the invariant too.

## Trade-Offs

An idempotency key makes retries safe, but the system must decide how long keys are stored and what request data is tied to each key.

A database unique constraint is reliable, but concurrent requests still need careful transaction handling.

A cache-only solution can be faster, but it is easier to lose state after restarts unless the cache is durable enough for the business risk.
