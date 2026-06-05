from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Order
from schemas import OrderCreate


def get_order_by_idempotency_key(session: Session, idempotency_key: str) -> Order | None:
    return session.execute(
        select(Order).where(Order.idempotency_key == idempotency_key)
    ).scalar_one_or_none()


def create_order(session: Session, payload: OrderCreate, idempotency_key: str) -> Order:
    existing_order = get_order_by_idempotency_key(
        session=session,
        idempotency_key=idempotency_key,
    )
    if existing_order is not None:
        return existing_order

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
