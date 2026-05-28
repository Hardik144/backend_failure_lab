import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from .repository import create_payment_attempt
from .schemas import PaymentResponse


logger = logging.getLogger("bfl_0005.broken")


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0005 Broken")

    @app.post(
        "/orders/{order_id}/pay",
        response_model=PaymentResponse,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    def pay_order(order_id: int) -> JSONResponse:
        attempt = create_payment_attempt(user_id=42, order_id=order_id)

        logger.error("Order not found")
        logger.error("Payment failed")
        logger.error("Database error")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "failed", "user_id": attempt.user_id},
        )

    return app
