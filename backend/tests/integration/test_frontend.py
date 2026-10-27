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
