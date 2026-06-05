from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Order


def get_order_for_user(session: Session, order_id: int, user_id: int) -> Order | None:
    return session.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    ).scalar_one_or_none()
