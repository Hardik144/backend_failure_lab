from pathlib import Path
import sys

import pytest
from sqlalchemy.exc import IntegrityError

CASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE_DIR))

from broken.app import create_app  # noqa: E402
from broken.repository import email_exists, insert_user_after_precheck  # noqa: E402


def test_database_rejects_duplicate_email_even_when_two_requests_pass_precheck(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'broken.db'}"
    app = create_app(database_url=database_url)
    email = "john@example.com"

    session_a = app.state.SessionLocal()
    session_b = app.state.SessionLocal()
    try:
        assert not email_exists(session=session_a, email=email)
        assert not email_exists(session=session_b, email=email)

        insert_user_after_precheck(session=session_a, email=email)
        session_a.commit()

        with pytest.raises(IntegrityError):
            insert_user_after_precheck(session=session_b, email=email)
            session_b.commit()
    finally:
        session_a.close()
        session_b.close()
