from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import create_order
from schemas import OrderCreate, OrderResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0003_fixed.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0003 Fixed")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
    def create_order_endpoint(
        payload: OrderCreate,
        session: Annotated[Session, Depends(get_session)],
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> OrderResponse:
        if not idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Idempotency-Key",
            )

        order = create_order(
            session=session,
            payload=payload,
            idempotency_key=idempotency_key,
        )
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            item_name=order.item_name,
            total_cents=order.total_cents,
        )

    return app
