from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402
from fixed.models import ...  # noqa: E402


@pytest.fixture
def client(tmp_path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    app = create_app(database_url=database_url)

    # TODO: seed test data via app.state.SessionLocal

    return TestClient(app)


def test_correct_behavior(client: TestClient) -> None:
    response = client.get("/your-endpoint")

    assert response.status_code == ...
    assert response.json() == ...
