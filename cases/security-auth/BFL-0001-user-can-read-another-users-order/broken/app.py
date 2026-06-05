from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import get_order_by_id
from schemas import OrderResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0001_broken.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0001 Broken")
    app.state.SessionLocal = SessionLocal

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def get_current_user_id(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    ) -> int:
        # This is a simplified auth mechanism for the lab case.
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-User-Id",
            )
        try:
            return int(x_user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid X-User-Id",
            ) from exc

    @app.get("/orders/{order_id}", response_model=OrderResponse)
    def read_order(
        order_id: int,
        current_user_id: Annotated[int, Depends(get_current_user_id)],
        session: Annotated[Session, Depends(get_session)],
    ) -> OrderResponse:
        _ = current_user_id
        order = get_order_by_id(session=session, order_id=order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            item_name=order.item_name,
            total_cents=order.total_cents,
        )

    return app

