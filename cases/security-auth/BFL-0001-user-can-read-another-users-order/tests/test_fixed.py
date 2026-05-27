from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402
from fixed.models import Order, User  # noqa: E402


@pytest.fixture
def client(tmp_path) -> TestClient:
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

    return TestClient(app)


def test_user_cannot_read_another_users_order(client: TestClient) -> None:
    response = client.get("/orders/100", headers={"X-User-Id": "2"})

    assert response.status_code == 404


def test_user_can_read_own_order(client: TestClient) -> None:
    response = client.get("/orders/100", headers={"X-User-Id": "1"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 100,
        "user_id": 1,
        "item_name": "Mechanical keyboard",
        "total_cents": 12900,
    }


def test_missing_user_header_returns_401(client: TestClient) -> None:
    response = client.get("/orders/100")

    assert response.status_code == 401
