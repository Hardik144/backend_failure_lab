from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import create_session_factory, init_database
import models  # noqa: F401 - imports models so metadata contains tables
from repository import DuplicateEmailError, create_user
from schemas import UserCreate, UserResponse


DEFAULT_DATABASE_URL = "sqlite:///./bfl_0010.db"


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    SessionLocal, engine = create_session_factory(database_url)
    init_database(engine)

    app = FastAPI(title="BFL-0010 Fixed")
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.post("/users", response_model=UserResponse, status_code=201)
    def register_user(
        payload: UserCreate,
        session: Annotated[Session, Depends(get_session)],
    ) -> UserResponse:
        try:
            return create_user(session=session, email=payload.email)
        except DuplicateEmailError as exc:
            raise HTTPException(status_code=409, detail="email already exists") from exc

    return app
