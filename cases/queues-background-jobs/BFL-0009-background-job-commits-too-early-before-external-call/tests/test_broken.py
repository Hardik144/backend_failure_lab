import httpx
import pytest

from app import create_app
from models import Order

@pytest.mark.asyncio
async def test_failed_notification_leaves_order_in_ghost_confirmed_state(tmp_path) -> None:
    # Endpoint returns 202 immediately (fire-and-forget).
    # Bug: broken/ commits status="confirmed" before calling the notification service.
    # When notification fails the DB already has a confirmed order — ghost state.
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    with app.state.SessionLocal() as session:
        session.add(Order(id=100, status="pending", confirmation_sent=False))
        session.commit()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/orders/100/confirm?fail_notification=true")
        stored = await client.get("/orders/100")

    assert response.status_code == 202
    # Expected: order stays pending because notification failed.
    # Actual in broken/: order is "confirmed" even though notification was never sent.
    assert stored.json() == {
        "id": 100,
        "status": "pending",
        "confirmation_sent": False,
    }
