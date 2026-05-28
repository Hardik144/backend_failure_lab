from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402
from fixed.models import Order, User  # noqa: E402


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


@pytest.fixture
def client(tmp_path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    app = create_app(database_url=database_url)

    with app.state.SessionLocal() as session:
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

    return TestClient(app)


def test_endpoint_returns_users_with_orders(client: TestClient) -> None:
    response = client.get("/users-with-orders")

    assert response.status_code == 200
    assert response.json()[0] == {
        "id": 1,
        "email": "user-1@example.com",
        "orders": [
            {
                "id": 100,
                "item_name": "Item 1",
                "total_cents": 1000,
            }
        ],
    }


def test_endpoint_uses_bounded_number_of_select_queries(client: TestClient) -> None:
    with count_select_queries(client.app.state.engine) as statements:
        response = client.get("/users-with-orders")

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert len(statements) <= 2
