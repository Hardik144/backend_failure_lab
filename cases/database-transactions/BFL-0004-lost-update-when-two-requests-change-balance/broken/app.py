from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .database import create_session_factory, init_database
from . import models  # noqa: F401 - imports models so metadata contains tables
from .repository import withdraw
from .schemas import AccountResponse, WithdrawRequest


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0004_broken.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0004 Broken")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
    def withdraw_from_account(
        account_id: int,
        payload: WithdrawRequest,
        session: Annotated[Session, Depends(get_session)],
    ) -> AccountResponse:
        account = withdraw(
            session=session,
            account_id=account_id,
            amount_cents=payload.amount_cents,
        )
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return AccountResponse(id=account.id, balance_cents=account.balance_cents)

    return app
