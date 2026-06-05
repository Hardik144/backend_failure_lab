from sqlalchemy.orm import Session

from models import Order


class NotificationServiceError(Exception):
    pass


def send_confirmation_notification(*, fail: bool) -> None:
    if fail:
        raise NotificationServiceError("notification service is unavailable")


def get_order(session: Session, order_id: int) -> Order | None:
    return session.get(Order, order_id)


def confirm_order(
    session: Session,
    order_id: int,
    *,
    fail_notification: bool = False,
) -> Order | None:
    order = get_order(session=session, order_id=order_id)
    if order is None:
        return None

    order.status = "confirmed"
    session.commit()

    send_confirmation_notification(fail=fail_notification)

    order.confirmation_sent = True
    session.commit()
    session.refresh(order)
    return order
