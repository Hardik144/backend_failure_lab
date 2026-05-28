from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Order
from .schemas import OrderCreate


def create_order(session: Session, payload: OrderCreate, idempotency_key: str) -> Order:
    order = Order(
        user_id=payload.user_id,
        item_name=payload.item_name,
        total_cents=payload.total_cents,
        idempotency_key=idempotency_key,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def count_orders(session: Session) -> int:
    return session.execute(select(func.count(Order.id))).scalar_one()
