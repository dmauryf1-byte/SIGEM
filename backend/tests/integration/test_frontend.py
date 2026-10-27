import pytest
from fastapi.testclient import TestClient


def test_raiz_sirve_el_login(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "SIGEM" in response.text


def test_api_sigue_respondiendo_con_estaticos_montados(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.headers["content-type"].startswith("application/json")
    assert response.status_code in (200, 503)


def test_ruta_inexistente_da_404(client: TestClient) -> None:
    assert client.get("/no-existe.html").status_code == 404


def test_sirve_css_y_js(client: TestClient) -> None:
    assert client.get("/css/sigem.css").status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/package.json",
        "/package-lock.json",
        "/eslint.config.js",
        "/node_modules/vitest/package.json",
        "/tests/unit/layout.test.js",
    ],
)
def test_no_expone_archivos_de_desarrollo(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 404
