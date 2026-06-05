import httpx
import pytest

from app import create_app
from models import Account
from repository import get_account, get_balance, withdraw

@pytest.fixture
def app(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'fixed.db'}"
    app = create_app(database_url=database_url)
    with app.state.SessionLocal() as session:
        session.add(Account(id=1, balance_cents=10000))
        session.commit()
    return app

def test_two_overlapping_withdrawals_apply_both_updates(app) -> None:
    session_a = app.state.SessionLocal()
    session_b = app.state.SessionLocal()
    try:
        stale_a = get_account(session=session_a, account_id=1)
        stale_b = get_account(session=session_b, account_id=1)

        assert stale_a is not None
        assert stale_b is not None

        withdraw(session=session_a, account_id=1, amount_cents=3000)
        withdraw(session=session_b, account_id=1, amount_cents=2000)
    finally:
        session_a.close()
        session_b.close()

    with app.state.SessionLocal() as session:
        final_balance = get_balance(session=session, account_id=1)

    assert final_balance == 5000

@pytest.mark.asyncio
async def test_withdraw_endpoint_returns_updated_balance(app) -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/accounts/1/withdraw", json={"amount_cents": 3000})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "balance_cents": 7000}
