import pytest
from fastapi.testclient import TestClient


from app import create_app
from models import ...


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
