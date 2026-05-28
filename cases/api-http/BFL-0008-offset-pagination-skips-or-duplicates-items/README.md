<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Offset Pagination Skips or Duplicates Items

## Summary

An API uses offset pagination for a changing list of orders.

It works while the dataset is stable. When new orders are inserted between page requests, the second page can contain duplicates or skip items.

## Metadata

- ID: `BFL-0008`
- Category: `api-http`
- Secondary categories: `database-transactions`, `performance-scaling`
- Level: `junior`
- Technologies: `python`, `fastapi`, `sqlalchemy`, `pytest`
- Failure modes: `stale-data`, `race-condition`
- Patterns: `cursor-pagination`
- Status: `draft`

## Problem

The API exposes an endpoint like this:

```http
GET /orders?limit=2&offset=2
```

The endpoint orders orders by newest first and then applies `OFFSET`.

This looks simple, but `OFFSET` is positional. If a new order is inserted before the client requests the next page, all later positions shift.

## Why This Happens in Production

Offset pagination is easy to implement and easy to explain, so it often appears in early API versions.

The problem is that production lists are rarely static. New rows are inserted, old rows are deleted, and filters can change while the client is paging. Offset pagination assumes that row positions stay stable between requests, but the database does not guarantee that for a changing result set.

## Broken Scenario

1. Existing orders are `5, 4, 3, 2, 1`, ordered newest first.
2. The client requests `GET /orders?limit=2&offset=0` and receives `5, 4`.
3. A new order `6` is inserted at the beginning of the list.
4. The client requests `GET /orders?limit=2&offset=2`.
5. The backend skips `6, 5` and returns `4, 3`.
6. Order `4` appears twice across pages.

## Broken Implementation

The broken implementation uses offset pagination:

```python
select(Order).order_by(Order.id.desc()).limit(limit).offset(offset)
```

This makes the second page depend on the current position of rows, not on the last item the client actually saw.

## Where the Bug Happens

The bug happens in the pagination contract.

The client thinks `offset=2` means "give me the next items after the two items I already saw". The database interprets it as "skip the first two rows in the current result set".

Those are not the same thing when new rows can appear between requests.

## How to Catch This Bug

Do not test pagination only on a static dataset.

A useful test should simulate a real paging flow:

1. request the first page;
2. insert a newer row;
3. request the second page;
4. check that pages do not overlap and that expected older items are still returned.

This catches the user-visible failure: duplicate or missing items across pages.

## Failing Test

The failing test reads the first page and gets orders `5, 4`.

Then it inserts order `6` and reads the second page with `offset=2`.

Safe behavior would return `3, 2`, because those are the next older orders after `4`.

The broken implementation returns `4, 3`, so the test fails.

## Diagnosis

The system fails because offset pagination uses a moving position as the page boundary.

A page boundary should be based on something stable from the previous response. For a newest-first order list, the stable boundary can be the last seen order ID.

That gives the next request a clear meaning: return orders older than the last order I already saw.

## Fixed Implementation

The fixed implementation uses cursor pagination:

```python
select(Order).where(Order.id < cursor).order_by(Order.id.desc()).limit(limit)
```

The first page has no cursor. The response includes `next_cursor`, which is the ID of the last item in the page.

The next request sends that cursor:

```http
GET /orders?limit=2&cursor=4
```

Now newly inserted order `6` does not affect the next page, because the query explicitly asks for orders with `id < 4`.

## How to Run

From the repository root:

### Broken Version

```bash
make broken CASE=BFL-0008
```

Expected result: this test is expected to fail because offset pagination duplicates an item after a new insert.

### Fixed Version

```bash
make fixed CASE=BFL-0008
```

Expected result: the tests should pass because cursor pagination uses a stable page boundary.

## Files

- `broken/` - implementation that uses `limit` and `offset`
- `fixed/` - implementation that uses cursor pagination by order ID
- `tests/` - tests that insert a new order between page requests

## Production Notes

Offset pagination can be acceptable for small admin screens, static datasets, or low-risk internal tools.

For user-facing feeds, order history, activity logs, and other changing lists, cursor pagination is usually safer. The cursor should be based on the same fields used for ordering.

Always define deterministic ordering. Pagination without a stable `ORDER BY` can produce inconsistent pages even without inserts.

## Trade-Offs

Offset pagination is simple and lets clients jump to page numbers, but it becomes unreliable and slower on large changing datasets.

Cursor pagination is more stable and often faster, but it does not naturally support arbitrary page numbers.

Using only `id` as a cursor is simple for this case. In real systems, a cursor may need multiple fields, such as `created_at` and `id`, to handle ties and preserve deterministic ordering.
