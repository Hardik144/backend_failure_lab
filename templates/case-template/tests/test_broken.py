from pathlib import Path
import sys

from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402
from broken.models import ...  # noqa: E402


def test_broken_behavior(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)

    # TODO: seed test data via app.state.SessionLocal

    client = TestClient(app)
    response = client.get("/your-endpoint")

    # This assertion is expected to FAIL with the broken implementation.
    assert response.status_code == ...
