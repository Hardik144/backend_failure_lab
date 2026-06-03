from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import create_session_factory, init_database
from . import models  # noqa: F401 - imports models so metadata contains tables
from .repository import NotificationServiceError, confirm_order, get_order
from .schemas import OrderResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0009.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0009 Broken")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.post("/orders/{order_id}/confirm", response_model=OrderResponse)
    def confirm_order_endpoint(
        order_id: int,
        session: Annotated[Session, Depends(get_session)],
        fail_notification: bool = False,
    ) -> OrderResponse:
        try:
            order = confirm_order(
                session=session,
                order_id=order_id,
                fail_notification=fail_notification,
            )
        except NotificationServiceError as exc:
            raise HTTPException(status_code=503, detail="notification failed") from exc

        if order is None:
            raise HTTPException(status_code=404, detail="order not found")
        return order

    @app.get("/orders/{order_id}", response_model=OrderResponse)
    def get_order_endpoint(
        order_id: int,
        session: Annotated[Session, Depends(get_session)],
    ) -> OrderResponse:
        order = get_order(session=session, order_id=order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="order not found")
        return order

    return app
