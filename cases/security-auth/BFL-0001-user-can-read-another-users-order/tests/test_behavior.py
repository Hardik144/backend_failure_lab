import httpx
import pytest

from app import create_app
from models import Order, User

@pytest.fixture
def app(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    app = create_app(database_url=database_url)

    with app.state.SessionLocal() as session:
        session.add_all(
            [
                User(id=1, email="user-a@example.com"),
                User(id=2, email="user-b@example.com"),
                Order(id=100, user_id=1, item_name="Mechanical keyboard", total_cents=12900),
            ]
        )
        session.commit()

    return app

@pytest.mark.asyncio
async def test_user_cannot_read_another_users_order(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/orders/100", headers={"X-User-Id": "2"})

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_can_read_own_order(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/orders/100", headers={"X-User-Id": "1"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 100,
        "user_id": 1,
        "item_name": "Mechanical keyboard",
        "total_cents": 12900,
    }

@pytest.mark.asyncio
async def test_missing_user_header_returns_401(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/orders/100")

    assert response.status_code == 401
