from app import create_app
from models import Account
from repository import get_account, get_balance, write_balance

def seed_account(session_factory) -> None:
    with session_factory() as session:
        session.add(Account(id=1, balance_cents=10000))
        session.commit()

def test_two_overlapping_withdrawals_do_not_lose_update(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    seed_account(app.state.SessionLocal)

    session_a = app.state.SessionLocal()
    session_b = app.state.SessionLocal()
    try:
        account_a = get_account(session=session_a, account_id=1)
        account_b = get_account(session=session_b, account_id=1)

        assert account_a is not None
        assert account_b is not None

        new_balance_a = account_a.balance_cents - 3000
        new_balance_b = account_b.balance_cents - 2000

        write_balance(session=session_a, account_id=1, balance_cents=new_balance_a)
        write_balance(session=session_b, account_id=1, balance_cents=new_balance_b)
    finally:
        session_a.close()
        session_b.close()

    with app.state.SessionLocal() as session:
        final_balance = get_balance(session=session, account_id=1)

    assert final_balance == 5000
