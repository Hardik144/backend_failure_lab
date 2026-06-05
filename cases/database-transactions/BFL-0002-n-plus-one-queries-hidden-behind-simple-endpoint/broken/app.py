from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import get_orders_for_user, get_users
from schemas import OrderResponse, UserWithOrdersResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0002_broken.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0002 Broken")
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
        users = get_users(session)
        response: list[UserWithOrdersResponse] = []

        for user in users:
            orders = get_orders_for_user(session=session, user_id=user.id)
            response.append(
                UserWithOrdersResponse(
                    id=user.id,
                    email=user.email,
                    orders=[
                        OrderResponse(
                            id=order.id,
                            item_name=order.item_name,
                            total_cents=order.total_cents,
                        )
                        for order in orders
                    ],
                )
            )

        return response

    return app
