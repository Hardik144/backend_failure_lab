from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Account


def get_account(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def withdraw(session: Session, account_id: int, amount_cents: int) -> Account | None:
    account = get_account(session=session, account_id=account_id)
    if account is None:
        return None

    account.balance_cents = account.balance_cents - amount_cents
    session.commit()
    session.refresh(account)
    return account


def write_balance(session: Session, account_id: int, balance_cents: int) -> None:
    account = get_account(session=session, account_id=account_id)
    if account is None:
        raise ValueError("account not found")
    account.balance_cents = balance_cents
    session.commit()


def get_balance(session: Session, account_id: int) -> int:
    return session.execute(
        select(Account.balance_cents).where(Account.id == account_id)
    ).scalar_one()
