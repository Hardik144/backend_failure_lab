from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import get_users_with_orders
from schemas import OrderResponse, UserWithOrdersResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0002_fixed.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0002 Fixed")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.get("/users-with-orders", response_model=list[UserWithOrdersResponse])
    def list_users_with_orders(
        session: Annotated[Session, Depends(get_session)],
    ) -> list[UserWithOrdersResponse]:
        users = get_users_with_orders(session)
        return [
            UserWithOrdersResponse(
                id=user.id,
                email=user.email,
                orders=[
                    OrderResponse(
                        id=order.id,
                        item_name=order.item_name,
                        total_cents=order.total_cents,
                    )
                    for order in user.orders
                ],
            )
            for user in users
        ]

    return app
