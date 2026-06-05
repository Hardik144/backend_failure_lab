from models import PaymentAttempt


def create_payment_attempt(user_id: int, order_id: int) -> PaymentAttempt:
    return PaymentAttempt(user_id=user_id, order_id=order_id)
