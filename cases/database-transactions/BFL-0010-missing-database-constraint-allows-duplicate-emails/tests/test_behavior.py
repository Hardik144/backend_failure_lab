import httpx
import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from repository import email_exists, insert_user_after_precheck

def test_database_rejects_duplicate_email_even_when_two_requests_pass_precheck(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    app = create_app(database_url=database_url)
    email = "john@example.com"

    session_a = app.state.SessionLocal()
    session_b = app.state.SessionLocal()
    try:
        assert not email_exists(session=session_a, email=email)
        assert not email_exists(session=session_b, email=email)

        insert_user_after_precheck(session=session_a, email=email)
        session_a.commit()

        with pytest.raises(IntegrityError):
            insert_user_after_precheck(session=session_b, email=email)
            session_b.commit()
    finally:
        session_a.close()
        session_b.close()

@pytest.mark.asyncio
async def test_endpoint_rejects_duplicate_email(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'api.db'}"
    app = create_app(database_url=database_url)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.post("/users", json={"email": "john@example.com"})
        second = await client.post("/users", json={"email": "john@example.com"})

    assert first.status_code == 201
    assert second.status_code == 409
