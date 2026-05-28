import asyncio
from pathlib import Path
import sys
import time

import httpx
import pytest

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402


REQUEST_COUNT = 3
MAX_EXPECTED_SECONDS = 0.16


@pytest.mark.asyncio
async def test_concurrent_requests_do_not_block_each_other() -> None:
    transport = httpx.ASGITransport(app=create_app())

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        started_at = time.perf_counter()
        responses = await asyncio.gather(
            *(client.get("/slow-operation") for _ in range(REQUEST_COUNT))
        )
        elapsed = time.perf_counter() - started_at

    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["status"] == "done" for response in responses)
    assert elapsed < MAX_EXPECTED_SECONDS
