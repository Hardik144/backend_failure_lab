from pathlib import Path
import sys

import httpx
import pytest

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402


@pytest.mark.asyncio
async def test_timed_out_request_does_not_complete_work() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/exports/100/run?simulate_timeout=true")
        stored = await client.get("/exports/100")

    assert response.status_code == 504
    assert stored.json() == {
        "id": 100,
        "status": "cancelled",
        "result": None,
    }
