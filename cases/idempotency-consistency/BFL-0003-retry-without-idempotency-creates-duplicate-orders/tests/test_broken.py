from pathlib import Path
import sys

from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402
from broken.repository import count_orders  # noqa: E402


PAYLOAD = {
    "user_id": 1,
    "item_name": "Noise-cancelling headphones",
    "total_cents": 19900,
}
HEADERS = {"Idempotency-Key": "same-command"}


def test_retry_with_same_idempotency_key_does_not_create_duplicate_order(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    client = TestClient(app)

    first_response = client.post("/orders", json=PAYLOAD, headers=HEADERS)
    second_response = client.post("/orders", json=PAYLOAD, headers=HEADERS)

    with app.state.SessionLocal() as session:
        total_orders = count_orders(session)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json()["id"] == first_response.json()["id"]
    assert total_orders == 1
