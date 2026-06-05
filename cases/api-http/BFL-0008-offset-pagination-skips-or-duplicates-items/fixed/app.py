from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from database import get_session
from repository import list_orders
from schemas import OrderListResponse, OrderResponse


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0008 Fixed")

    @app.get("/orders", response_model=OrderListResponse)
    def get_orders(
        limit: int = Query(default=2, ge=1, le=50),
        cursor: int | None = Query(default=None, ge=1),
        session: Session = Depends(get_session),
    ) -> OrderListResponse:
        orders = list_orders(session, limit=limit, cursor=cursor)
        next_cursor = orders[-1].id if orders else None
        return OrderListResponse(
            items=[OrderResponse(id=order.id, item_name=order.item_name) for order in orders],
            next_cursor=next_cursor,
        )

    return app
