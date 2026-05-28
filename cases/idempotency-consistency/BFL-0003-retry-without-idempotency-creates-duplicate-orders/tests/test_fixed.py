from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402
from fixed.repository import count_orders  # noqa: E402


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


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def test_retry_with_same_idempotency_key_returns_existing_order(client: TestClient, app) -> None:
    first_response = client.post("/orders", json=PAYLOAD, headers=HEADERS)
    second_response = client.post("/orders", json=PAYLOAD, headers=HEADERS)

    with app.state.SessionLocal() as session:
        total_orders = count_orders(session)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()
    assert total_orders == 1


def test_missing_idempotency_key_returns_400(client: TestClient) -> None:
    response = client.post("/orders", json=PAYLOAD)

    assert response.status_code == 400
