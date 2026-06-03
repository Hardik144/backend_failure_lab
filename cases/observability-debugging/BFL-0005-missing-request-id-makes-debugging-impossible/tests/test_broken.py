import logging
from pathlib import Path
import sys

import httpx
import pytest

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402


@pytest.mark.asyncio
async def test_response_and_logs_include_request_id(caplog) -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    request_id = "abc-123"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        with caplog.at_level(logging.ERROR, logger="bfl_0005.broken"):
            response = await client.post(
                "/orders/100/pay",
                headers={"X-Request-ID": request_id},
            )

    log_messages = [record.getMessage() for record in caplog.records]

    assert response.status_code == 500
    assert response.headers.get("X-Request-ID") == request_id
    assert log_messages
    assert all(f"request_id={request_id}" in message for message in log_messages)
