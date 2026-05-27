from pathlib import Path
import sys

from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402
from broken.models import Order, User  # noqa: E402


def seed_data(session_factory) -> None:
    with session_factory() as session:
        session.add_all(
            [
                User(id=1, email="user-a@example.com"),
                User(id=2, email="user-b@example.com"),
                Order(id=100, user_id=1, item_name="Mechanical keyboard", total_cents=12900),
            ]
        )
        session.commit()


def test_user_cannot_read_another_users_order(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    seed_data(app.state.SessionLocal)

    client = TestClient(app)
    response = client.get("/orders/100", headers={"X-User-Id": "2"})

    assert response.status_code == 404
