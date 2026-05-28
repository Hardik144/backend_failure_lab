<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Blocking Code Inside Async Endpoint

## Summary

A FastAPI endpoint is declared with `async def`, but it calls blocking code inside the request handler.

The endpoint looks asynchronous, but `time.sleep()` blocks the event loop. When several requests arrive at the same time, they are processed one after another instead of making progress concurrently.

## Metadata

- ID: `BFL-0007`
- Category: `performance-scaling`
- Secondary category: `api-http`
- Level: `junior`
- Technologies: `python`, `fastapi`, `pytest`
- Failure modes: `blocking-async-code`, `timeout`
- Status: `draft`

## Problem

The API exposes an endpoint that simulates slow work.

The broken implementation is written as an async endpoint:

```python
@app.get("/slow-operation")
async def slow_operation():
    time.sleep(0.08)
    return {"status": "done"}
```

The `async def` part is not enough. The blocking call still runs on the event loop thread, so the event loop cannot switch to other requests while `time.sleep()` is running.

## Why This Happens in Production

This bug is common when developers start using FastAPI and assume that every `async def` endpoint is automatically non-blocking.

In reality, async code only helps when the code inside the coroutine cooperates with the event loop. Calls like `time.sleep()`, synchronous HTTP clients, slow file operations, and CPU-heavy work can still block all other coroutines on the same event loop.

## Broken Scenario

1. Three clients send `GET /slow-operation` at the same time.
2. The endpoint starts handling the first request.
3. The endpoint calls `time.sleep()`.
4. The event loop is blocked and cannot make progress on the other requests.
5. The requests finish roughly one after another.

## Broken Implementation

The broken implementation blocks inside an async endpoint:

```python
time.sleep(WORK_SECONDS)
```

This line pauses the whole event loop thread. It does not only pause the current request.

## Where the Bug Happens

The bug happens at the boundary between async request handling and synchronous blocking work.

`async def` creates a coroutine, but it does not magically make every function inside it asynchronous. If the code calls a blocking function, the event loop cannot run other scheduled tasks until that function returns.

## How to Catch This Bug

A single-request test will usually miss this problem because one request still returns successfully.

A better test sends several requests concurrently and measures the total time. If three requests take about three times as long as one request, the endpoint is probably blocking the event loop.

This kind of test does not need exact production timing. It only needs to prove the shape of the failure: concurrent requests behave like sequential requests.

## Failing Test

The failing test sends three concurrent requests to `GET /slow-operation`.

Safe behavior is that the total time stays close to one simulated delay, because all requests should wait concurrently.

The broken implementation uses `time.sleep()`, so the requests run mostly one after another and the test fails.

## Diagnosis

The system fails because blocking code is running on the event loop.

The event loop is responsible for switching between pending async tasks. When a task calls `time.sleep()`, the event loop thread is occupied and cannot switch to other requests.

The result is poor concurrency: the service may look fine under one request, but latency grows quickly when several requests arrive at once.

## Fixed Implementation

The fixed implementation uses a non-blocking awaitable delay:

```python
await asyncio.sleep(WORK_SECONDS)
```

`asyncio.sleep()` tells the event loop that this coroutine is waiting and can be paused. While it waits, the event loop can continue processing other requests.

If the real work is blocking and cannot be replaced with an async library, use a thread pool for short blocking I/O or move long work to a background job. The important rule is that the event loop should not run blocking work directly.

## How to Run

From the repository root:

### Broken Version

```bash
make broken CASE=BFL-0007
```

Expected result: this test is expected to fail because concurrent requests are handled too slowly.

### Fixed Version

```bash
make fixed CASE=BFL-0007
```

Expected result: the tests should pass because the fixed implementation yields control back to the event loop.

## Files

- `broken/` - implementation that calls `time.sleep()` inside an async endpoint
- `fixed/` - implementation that uses `await asyncio.sleep()`
- `tests/` - tests that compare concurrent request timing

## Production Notes

Blocking code in async endpoints can cause timeouts, queue buildup, and unpredictable latency under load.

Common sources are `time.sleep()`, synchronous database drivers, synchronous HTTP clients, slow filesystem calls, image processing, and CPU-heavy calculations.

For I/O, prefer async-compatible libraries when the surrounding stack is async. For unavoidable blocking work, isolate it with a thread pool or move it out of the request path.

## Trade-Offs

`await asyncio.sleep()` is the right fix for this lab because the slow work is only a simulated wait.

In real systems, replacing a blocking client with an async client may require more changes, but it keeps request handling scalable.

A thread pool can be pragmatic for small blocking operations, but it is not a free scalability solution. Long CPU-heavy work should usually be moved to a worker process or background job.
