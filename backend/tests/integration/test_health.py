from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.db import get_session
from app.main import app


def test_health_ok_con_mysql_arriba(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200, (
        f"MySQL no respondió ({response.json()}). ¿Está arriba? docker compose up -d mysql"
    )
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_503_con_mysql_caido(client: TestClient) -> None:
    # Puerto 1: nada escucha ahí, la conexión se rechaza de inmediato
    dead_url = settings.database_url().set(port=1)
    dead_session = sessionmaker(bind=create_engine(dead_url, connect_args={"connect_timeout": 2}))

    def get_dead_session() -> Iterator[Session]:
        with dead_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_dead_session

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    body = response.json()
    assert body["errors"][0]["code"] == "database_unavailable"
    assert body["errors"][0]["message"] == "La base de datos no responde"
    assert "Traceback" not in response.text
    assert "pymysql" not in response.text.lower()
