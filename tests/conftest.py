import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from sentiment_app.db import get_session
from sentiment_app.main import app


@pytest.fixture
def client():
    # Fresh in-memory database per test: fast, isolated, never touches real data
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    with TestClient(app) as test_client:  # "with" runs the lifespan, so the model loads
        yield test_client
    app.dependency_overrides.clear()
