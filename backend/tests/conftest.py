from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.db import Base, get_session
from app.main import app

TEST_DATABASE = "sigem_test"
ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

test_engine = create_engine(settings.database_url(TEST_DATABASE), pool_pre_ping=True)
TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def get_test_session() -> Iterator[Session]:
    with TestSession() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def migrated_test_database() -> None:
    """Aplica las migraciones reales a sigem_test una vez por corrida (MySQL real, nunca SQLite)."""
    config = Config(str(ALEMBIC_INI))
    config.attributes["database"] = TEST_DATABASE
    command.upgrade(config, "head")


@pytest.fixture(autouse=True)
def clean_tables() -> Iterator[None]:
    yield
    with test_engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in Base.metadata.sorted_tables:
            connection.execute(text(f"TRUNCATE TABLE `{table.name}`"))
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


@pytest.fixture
def db() -> Iterator[Session]:
    with TestSession() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente contra la app usando la base sigem_test."""
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
