from pathlib import Path
import sys

import httpx
import pytest

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402
from fixed.database import SessionLocal, reset_database  # noqa: E402
from fixed.repository import get_redis_client, profile_cache_key, seed_profile  # noqa: E402


def prepare_state() -> None:
    reset_database()
    redis_client = get_redis_client()
    redis_client.delete(profile_cache_key(1))

    with SessionLocal() as session:
        seed_profile(session, user_id=1, name="Old Name")


@pytest.mark.asyncio
async def test_profile_update_invalidates_cached_value() -> None:
    prepare_state()
    headers = {"X-User-Id": "1"}
    transport = httpx.ASGITransport(app=create_app())

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first_response = await client.get("/profile", headers=headers)
        update_response = await client.patch(
            "/profile",
            headers=headers,
            json={"name": "Jhon"},
        )
        second_response = await client.get("/profile", headers=headers)

    assert first_response.status_code == 200
    assert first_response.json()["name"] == "Old Name"
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Jhon"
    assert second_response.status_code == 200
    assert second_response.json()["name"] == "Jhon"


@pytest.mark.asyncio
async def test_missing_user_header_returns_401() -> None:
    prepare_state()
    transport = httpx.ASGITransport(app=create_app())

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/profile")

    assert response.status_code == 401
