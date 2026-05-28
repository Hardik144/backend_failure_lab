from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .models import Account


def get_account(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def withdraw(session: Session, account_id: int, amount_cents: int) -> Account | None:
    result = session.execute(
        update(Account)
        .where(Account.id == account_id)
        .values(balance_cents=Account.balance_cents - amount_cents)
    )
    if result.rowcount == 0:
        session.rollback()
        return None

    session.commit()
    return get_account(session=session, account_id=account_id)


def get_balance(session: Session, account_id: int) -> int:
    return session.execute(
        select(Account.balance_cents).where(Account.id == account_id)
    ).scalar_one()
