from __future__ import annotations

import json
import os
from typing import Any

from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import UserProfile


CACHE_TTL_SECONDS = 300


def get_redis_client() -> Redis:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(redis_url, decode_responses=True)


def profile_cache_key(user_id: int) -> str:
    return f"profile:{user_id}"


def serialize_profile(profile: UserProfile) -> dict[str, Any]:
    return {"user_id": profile.user_id, "name": profile.name}


def seed_profile(session: Session, user_id: int, name: str) -> UserProfile:
    profile = UserProfile(user_id=user_id, name=name)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_profile_from_database(session: Session, user_id: int) -> UserProfile | None:
    return session.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).scalar_one_or_none()


def get_profile(session: Session, redis_client: Redis, user_id: int) -> dict[str, Any] | None:
    cache_key = profile_cache_key(user_id)
    cached_profile = redis_client.get(cache_key)
    if cached_profile is not None:
        return json.loads(cached_profile)

    profile = get_profile_from_database(session, user_id)
    if profile is None:
        return None

    data = serialize_profile(profile)
    redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL_SECONDS)
    return data


def update_profile_name(session: Session, user_id: int, name: str) -> dict[str, Any] | None:
    profile = get_profile_from_database(session, user_id)
    if profile is None:
        return None

    profile.name = name
    session.commit()
    session.refresh(profile)
    return serialize_profile(profile)

