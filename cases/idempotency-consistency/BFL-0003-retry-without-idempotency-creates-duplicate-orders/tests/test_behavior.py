import httpx
import pytest

from app import create_app
from repository import count_orders

PAYLOAD = {
    "user_id": 1,
    "item_name": "Noise-cancelling headphones",
    "total_cents": 19900,
}
HEADERS = {"Idempotency-Key": "same-command"}

@pytest.fixture
def app(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    return create_app(database_url=database_url)

@pytest.mark.asyncio
async def test_retry_with_same_idempotency_key_returns_existing_order(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first_response = await client.post("/orders", json=PAYLOAD, headers=HEADERS)
        second_response = await client.post("/orders", json=PAYLOAD, headers=HEADERS)

    with app.state.SessionLocal() as session:
        total_orders = count_orders(session)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()
    assert total_orders == 1

@pytest.mark.asyncio
async def test_missing_idempotency_key_returns_400(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/orders", json=PAYLOAD)

    assert response.status_code == 400
