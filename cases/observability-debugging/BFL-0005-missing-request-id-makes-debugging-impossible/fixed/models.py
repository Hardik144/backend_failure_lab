from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentAttempt:
    user_id: int
    order_id: int
