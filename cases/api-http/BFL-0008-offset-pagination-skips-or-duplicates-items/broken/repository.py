from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order


def seed_orders(session: Session, order_ids: list[int]) -> None:
    for order_id in order_ids:
        session.add(Order(id=order_id, item_name=f"Order #{order_id}"))
    session.commit()


def insert_order(session: Session, order_id: int) -> None:
    session.add(Order(id=order_id, item_name=f"Order #{order_id}"))
    session.commit()


def list_orders(session: Session, limit: int, offset: int) -> list[Order]:
    return list(
        session.execute(
            select(Order).order_by(Order.id.desc()).limit(limit).offset(offset)
        ).scalars()
    )
