from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_session
from .repository import get_profile, get_redis_client, update_profile_name
from .schemas import ProfileResponse, ProfileUpdate


def get_current_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> int:
    # This is a simplified auth mechanism for the lab case.
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id")

    try:
        return int(x_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id",
        ) from exc


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0006 Broken")

    @app.get("/profile", response_model=ProfileResponse)
    def read_profile(
        current_user_id: int = Depends(get_current_user_id),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        redis_client = get_redis_client()
        profile = get_profile(session, redis_client, current_user_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return profile

    @app.patch("/profile", response_model=ProfileResponse)
    def update_profile(
        payload: ProfileUpdate,
        current_user_id: int = Depends(get_current_user_id),
        session: Session = Depends(get_session),
    ) -> dict[str, object]:
        profile = update_profile_name(session, current_user_id, payload.name)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        return profile

    return app
