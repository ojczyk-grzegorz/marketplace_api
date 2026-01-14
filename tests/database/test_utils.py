from sqlmodel import Session

from app.database.utils import get_db_session


def test_get_db_session() -> None:
    with next(get_db_session()) as session:
        assert isinstance(session, Session)
