from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import User


class DuplicateEmailError(Exception):
    pass


def email_exists(session: Session, email: str) -> bool:
    return session.execute(select(User).where(User.email == email)).first() is not None


def insert_user_after_precheck(session: Session, email: str) -> User:
    user = User(email=email)
    session.add(user)
    session.flush()
    return user


def create_user(session: Session, email: str) -> User:
    if email_exists(session=session, email=email):
        raise DuplicateEmailError("email already exists")

    try:
        user = insert_user_after_precheck(session=session, email=email)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise DuplicateEmailError("email already exists") from exc

    session.refresh(user)
    return user
