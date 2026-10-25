from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.db import get_session
from app.main import app

TEST_DATABASE = "sigem_test"

test_engine = create_engine(settings.database_url(TEST_DATABASE), pool_pre_ping=True)
TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def get_test_session() -> Iterator[Session]:
    with TestSession() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente contra la app usando la base sigem_test (MySQL real, nunca SQLite)."""
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
