from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import NotificationServiceError, confirm_order, get_order
from schemas import OrderResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0009.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0009 Fixed")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def _run_confirm(order_id: int, fail_notification: bool) -> None:
        with SessionLocal() as session:
            try:
                confirm_order(session=session, order_id=order_id, fail_notification=fail_notification)
            except NotificationServiceError:
                pass  # fire-and-forget: caller already received 202

    @app.post("/orders/{order_id}/confirm", status_code=202)
    def confirm_order_endpoint(
        order_id: int,
        session: Annotated[Session, Depends(get_session)],
        background_tasks: BackgroundTasks,
        fail_notification: bool = False,
    ) -> dict:
        order = get_order(session=session, order_id=order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="order not found")
        background_tasks.add_task(_run_confirm, order_id, fail_notification)
        return {"message": "accepted"}

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
