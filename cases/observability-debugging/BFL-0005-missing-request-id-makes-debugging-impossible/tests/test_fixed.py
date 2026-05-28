import json
import logging
from pathlib import Path
import sys

from fastapi.testclient import TestClient

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from fixed.app import create_app  # noqa: E402


def test_response_and_logs_include_same_request_id(caplog) -> None:
    app = create_app()
    client = TestClient(app)
    request_id = "abc-123"

    with caplog.at_level(logging.ERROR, logger="bfl_0005.fixed"):
        response = client.post("/orders/100/pay", headers={"X-Request-ID": request_id})

    events = [json.loads(record.getMessage()) for record in caplog.records]

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == request_id
    assert [event["event"] for event in events] == [
        "order_not_found",
        "payment_failed",
        "database_error",
    ]
    assert all(event["request_id"] == request_id for event in events)
    assert all(event["user_id"] == 42 for event in events)
    assert all(event["order_id"] == 100 for event in events)


def test_missing_request_id_is_generated_and_logged(caplog) -> None:
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.ERROR, logger="bfl_0005.fixed"):
        response = client.post("/orders/100/pay")

    generated_request_id = response.headers["X-Request-ID"]
    events = [json.loads(record.getMessage()) for record in caplog.records]

    assert response.status_code == 500
    assert generated_request_id
    assert all(event["request_id"] == generated_request_id for event in events)
