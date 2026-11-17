# db.py
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from sentiment_app.config import get_settings

_url = get_settings().sqlalchemy_url
_connect_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}

# pool_pre_ping re-opens connections that a scale-to-zero database closed while idle
engine = create_engine(_url, pool_pre_ping=True, connect_args=_connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
