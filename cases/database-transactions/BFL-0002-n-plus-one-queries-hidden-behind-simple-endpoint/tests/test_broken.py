from collections.abc import Iterator
from contextlib import contextmanager

import httpx
import pytest
from sqlalchemy import event

from app import create_app
from models import Order, User

@contextmanager
def count_select_queries(engine) -> Iterator[list[str]]:
    statements: list[str] = []

    def before_cursor_execute(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

def seed_data(session_factory) -> None:
    with session_factory() as session:
        for user_id in range(1, 6):
            session.add(User(id=user_id, email=f"user-{user_id}@example.com"))
            session.add(
                Order(
                    id=user_id * 100,
                    user_id=user_id,
                    item_name=f"Item {user_id}",
                    total_cents=user_id * 1000,
                )
            )
        session.commit()

@pytest.mark.asyncio
async def test_endpoint_does_not_use_n_plus_one_queries(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    seed_data(app.state.SessionLocal)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        with count_select_queries(app.state.engine) as statements:
            response = await client.get("/users-with-orders")

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert len(statements) <= 2
