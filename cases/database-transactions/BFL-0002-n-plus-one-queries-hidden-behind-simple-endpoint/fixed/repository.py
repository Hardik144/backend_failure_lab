from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import User


def get_users_with_orders(session: Session) -> list[User]:
    return list(
        session.execute(
            select(User).options(selectinload(User.orders)).order_by(User.id)
        ).scalars()
    )
