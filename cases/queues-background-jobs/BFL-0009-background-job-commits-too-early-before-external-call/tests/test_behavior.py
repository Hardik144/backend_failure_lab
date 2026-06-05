import httpx
import pytest

from app import create_app
from models import Order

def seed_order(app) -> None:
    with app.state.SessionLocal() as session:
        session.add(Order(id=100, status="pending", confirmation_sent=False))
        session.commit()

@pytest.mark.asyncio
async def test_failed_notification_leaves_order_pending(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'fail.db'}"
    app = create_app(database_url=database_url)
    seed_order(app)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/orders/100/confirm?fail_notification=true")
        stored = await client.get("/orders/100")

    assert response.status_code == 202
    assert stored.json() == {
        "id": 100,
        "status": "pending",
        "confirmation_sent": False,
    }

@pytest.mark.asyncio
async def test_successful_notification_confirms_order(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'success.db'}"
    app = create_app(database_url=database_url)
    seed_order(app)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/orders/100/confirm")
        stored = await client.get("/orders/100")

    assert response.status_code == 202
    assert stored.json() == {
        "id": 100,
        "status": "confirmed",
        "confirmation_sent": True,
    }
