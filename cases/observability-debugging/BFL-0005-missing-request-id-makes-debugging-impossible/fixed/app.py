import json
import logging
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from repository import create_payment_attempt
from schemas import PaymentResponse


logger = logging.getLogger("bfl_0005.fixed")


def log_event(event: str, request_id: str, user_id: int, order_id: int) -> None:
    logger.error(
        json.dumps(
            {
                "event": event,
                "request_id": request_id,
                "user_id": user_id,
                "order_id": order_id,
            },
            sort_keys=True,
        )
    )


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0005 Fixed")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.post(
        "/orders/{order_id}/pay",
        response_model=PaymentResponse,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    def pay_order(order_id: int, request: Request) -> JSONResponse:
        attempt = create_payment_attempt(user_id=42, order_id=order_id)
        request_id = request.state.request_id

        log_event("order_not_found", request_id, attempt.user_id, attempt.order_id)
        log_event("payment_failed", request_id, attempt.user_id, attempt.order_id)
        log_event("database_error", request_id, attempt.user_id, attempt.order_id)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "failed", "user_id": attempt.user_id},
        )

    return app
