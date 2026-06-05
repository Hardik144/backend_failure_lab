from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Order, User


def get_users(session: Session) -> list[User]:
    return list(session.execute(select(User).order_by(User.id)).scalars())


def get_orders_for_user(session: Session, user_id: int) -> list[Order]:
    return list(
        session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.id)
        ).scalars()
    )
