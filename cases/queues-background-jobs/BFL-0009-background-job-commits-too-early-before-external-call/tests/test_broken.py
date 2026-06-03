from pathlib import Path
import sys

import httpx
import pytest

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402
from broken.models import Order  # noqa: E402


@pytest.mark.asyncio
async def test_failed_external_call_does_not_confirm_order(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    with app.state.SessionLocal() as session:
        session.add(Order(id=100, status="pending", confirmation_sent=False))
        session.commit()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/orders/100/confirm?fail_notification=true")
        stored = await client.get("/orders/100")

    assert response.status_code == 503
    assert stored.json() == {
        "id": 100,
        "status": "pending",
        "confirmation_sent": False,
    }
