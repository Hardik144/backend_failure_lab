import httpx
import pytest

from app import create_app
from database import SessionLocal, reset_database
from repository import insert_order, seed_orders

def prepare_state() -> None:
    reset_database()
    with SessionLocal() as session:
        seed_orders(session, [1, 2, 3, 4, 5])

def add_newest_order() -> None:
    with SessionLocal() as session:
        insert_order(session, 6)

@pytest.mark.asyncio
async def test_offset_pagination_does_not_duplicate_items_after_insert() -> None:
    prepare_state()
    transport = httpx.ASGITransport(app=create_app())

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first_page = await client.get("/orders", params={"limit": 2, "offset": 0})
        add_newest_order()
        second_page = await client.get("/orders", params={"limit": 2, "offset": 2})

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert [item["id"] for item in first_page.json()["items"]] == [5, 4]
    assert [item["id"] for item in second_page.json()["items"]] == [3, 2]
