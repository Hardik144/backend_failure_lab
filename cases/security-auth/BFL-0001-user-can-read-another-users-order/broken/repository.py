from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order


def get_order_by_id(session: Session, order_id: int) -> Order | None:
    return session.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
