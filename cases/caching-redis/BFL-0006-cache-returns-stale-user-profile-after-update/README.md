<p align="right">
  <a href="README.md">English</a> |
  <a href="README.ru.md">Русский</a>
</p>

# Cache Returns Stale User Profile After Update

## Summary

A user updates their profile, but the API keeps returning the old profile from Redis cache.

The database contains the correct value. The response is wrong because the cached value was not invalidated after the write.

## Metadata

- ID: `BFL-0006`
- Category: `caching-redis`
- Secondary category: `idempotency-consistency`
- Level: `junior`
- Technologies: `python`, `fastapi`, `sqlalchemy`, `redis`, `pytest`, `docker-compose`
- Failure modes: `stale-data`
- Status: `draft`

## Problem

The API has two endpoints:

- `GET /profile` reads the current user's profile and stores it in Redis cache;
- `PATCH /profile` updates the profile name in the database.

The broken implementation updates the database but leaves the old Redis value untouched. The next `GET /profile` hits the cache and returns stale data.

This creates a confusing production symptom: the database is correct, but the API response is not.

## Why This Happens in Production

This bug often appears when reads are optimized with cache, but writes are implemented as if the cache does not exist.

The write path and read path become inconsistent. The read path uses Redis, the write path updates only the database, and the cache keeps serving an older snapshot until TTL expires or someone clears it manually.

## Broken Scenario

1. User `1` has profile name `Old Name` in the database.
2. User `1` sends `GET /profile`.
3. The backend reads the profile from the database and writes `Old Name` to Redis.
4. User `1` sends `PATCH /profile` with `name = "Jhon"`.
5. The backend updates the database.
6. The Redis key still contains `Old Name`.
7. The next `GET /profile` returns `Old Name` from cache.

## Broken Implementation

The broken implementation follows a cache-aside read path:

```python
cached_profile = redis_client.get(cache_key)
if cached_profile:
    return cached_profile

profile = get_profile_from_database(user_id)
redis_client.set(cache_key, profile, ex=ttl)
return profile
```

But the update path only changes the database:

```python
update_profile_name(user_id=user_id, name="Jhon")
```

The missing step is cache invalidation after the database write succeeds.

## Where the Bug Happens

The bug happens in the write path, not in Redis itself.

Redis is doing exactly what the code asked it to do: store and return a value. The backend is wrong because it changes the source of truth without removing or replacing the cached copy.

When a value is cached on read and changed on write, the write code must define what happens to the cache key. Leaving the key untouched means future reads can observe old state.

## How to Catch This Bug

Do not test `GET /profile` and `PATCH /profile` separately only.

The useful test is the full read-write-read flow:

1. read the profile once to populate the cache;
2. update the profile;
3. read the profile again;
4. assert that the second read returns the new value.

This catches the exact user-visible failure: stale data after a successful update.

## Failing Test

The failing test creates a profile with `name = "Old Name"`.

Then it calls:

```text
GET /profile
PATCH /profile {"name": "Jhon"}
GET /profile
```

Safe behavior is that the final `GET /profile` returns `name = "Jhon"`.

The broken implementation returns `name = "Old Name"`, so the test fails.

## Diagnosis

The system fails because the read model and write model are not coordinated.

The database is the source of truth, but Redis is allowed to answer reads. Once Redis contains a profile snapshot, the backend must either invalidate that snapshot after an update or replace it with a fresh value.

TTL is not a correctness strategy. TTL can limit how long stale data survives, but users can still see wrong data before the key expires.

## Fixed Implementation

The fixed implementation deletes the profile cache key after the database update commits:

```python
updated_profile = update_profile_name(db, user_id=current_user_id, name=payload.name)
delete_profile_cache(redis_client, user_id=current_user_id)
return updated_profile
```

Deleting the key is a small and reliable cache-aside fix. The next `GET /profile` misses Redis, reloads the fresh profile from the database, and writes the new value back to cache.

Another valid approach is to update the Redis value immediately after the database write. For this case, deletion is easier to reason about: the database remains the source of truth, and the cache is rebuilt by the normal read path.

## How to Run

From the repository root:

### Broken Version

```bash
make broken CASE=BFL-0006
```

Expected result: this test is expected to fail because the broken implementation returns the old cached profile after update.

### Fixed Version

```bash
make fixed CASE=BFL-0006
```

Expected result: the tests should pass because the fixed implementation invalidates the Redis key after update.

This case requires Redis. The Docker runner starts the Redis service through `docker compose`.

## Files

- `broken/` - implementation that updates the database but leaves stale cache behind
- `fixed/` - implementation that invalidates the profile cache after update
- `tests/` - tests for the read-write-read cache behavior

## Production Notes

Cache invalidation must be part of the write path design. If a write changes data that a cached read can return, the write must delete or refresh the related cache key.

Use stable and predictable cache keys. In this case the key is `profile:{user_id}`, which makes it clear which key must be invalidated when a user's own profile changes.

Be careful with TTL-based thinking. TTL is useful as a fallback, but it should not be the only mechanism that makes updated data visible.

## Trade-Offs

Deleting the cache key is simple and safe, but the next read has to hit the database.

Updating the cache immediately avoids a database read on the next request, but it duplicates serialization logic in the write path and can become harder to keep consistent.

Short TTLs reduce the duration of stale data, but increase cache churn and still allow incorrect responses before expiration.
