"""Pruebas del servidor Flask: pantallas, archivos estáticos y puente hacia la API."""

import io
from email.message import Message
from typing import Any
from urllib.error import HTTPError, URLError

import pytest
from flask.testing import FlaskClient

import app as web


@pytest.fixture
def client() -> FlaskClient:
    return web.app.test_client()


# ─── Pantallas ────────────────────────────────────────────────────────────────
def test_la_raiz_muestra_el_login(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    assert "Iniciar sesión" in response.text


@pytest.mark.parametrize("page", sorted(web.PAGES))
def test_cada_pantalla_existe_y_tiene_el_nombre_sigem(client: FlaskClient, page: str) -> None:
    response = client.get(f"/{page}.html")
    assert response.status_code == 200
    assert "SIGEM" in response.text


def test_las_pantallas_con_facturas_avisan_que_no_es_factura_dian(client: FlaskClient) -> None:
    for page in ("index", "facturas", "factura-nueva"):
        assert "DIAN" in client.get(f"/{page}.html").text


def test_sirve_css_y_js(client: FlaskClient) -> None:
    assert client.get("/css/sigem.css").status_code == 200
    assert client.get("/js/shared/layout.js").status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/no-existe.html",
        "/package.json",
        "/eslint.config.js",
        "/node_modules/vitest/package.json",
        "/tests/unit/layout.test.js",
        "/js/../package.json",
        "/css/..%2Fpackage.json",
    ],
)
def test_no_expone_archivos_de_desarrollo(client: FlaskClient, path: str) -> None:
    assert client.get(path).status_code == 404


# ─── Puente hacia la API ──────────────────────────────────────────────────────
class FakeUpstream:
    """Imita la respuesta de urlopen para no depender de que FastAPI esté encendido."""

    def __init__(self, status: int, body: bytes, headers: Message) -> None:
        self.status, self.body, self.headers = status, body, headers

    def read(self) -> bytes:
        return self.body

    def __enter__(self) -> "FakeUpstream":
        return self

    def __exit__(self, *_: object) -> None:
        return None


def make_headers(cookies: list[str]) -> Message:
    headers = Message()
    headers["Content-Type"] = "application/json"
    for cookie in cookies:
        headers["Set-Cookie"] = cookie
    return headers


def test_reenvia_metodo_cuerpo_cookies_y_query(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    sent: dict[str, Any] = {}
    cookies = ["access=a; HttpOnly; Path=/api/v1", "refresh=r; HttpOnly; Path=/api/v1/auth"]

    def fake_urlopen(req: Any, timeout: int) -> FakeUpstream:
        sent.update(url=req.full_url, method=req.method, body=req.data)
        sent["cookie"] = req.get_header("Cookie")
        return FakeUpstream(200, b'{"ok": true}', make_headers(cookies))

    monkeypatch.setattr(web, "urlopen", fake_urlopen)
    client.set_cookie("access", "viejo")
    response = client.post("/api/v1/auth/login?x=1", json={"username": "ana"})

    assert sent["url"] == f"{web.API_URL}/api/v1/auth/login?x=1"
    assert sent["method"] == "POST"
    assert sent["body"] == b'{"username": "ana"}'
    assert sent["cookie"] == "access=viejo"
    assert response.status_code == 200
    assert response.json == {"ok": True}
    assert response.headers.getlist("Set-Cookie") == cookies


def test_los_errores_de_la_api_llegan_tal_cual(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = b'{"errors": [{"field": null, "code": "invalid_credentials", "message": "x"}]}'

    def fake_urlopen(req: Any, timeout: int) -> FakeUpstream:
        raise HTTPError(req.full_url, 401, "Unauthorized", make_headers([]), io.BytesIO(body))

    monkeypatch.setattr(web, "urlopen", fake_urlopen)
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.data == body


def test_backend_apagado_responde_502_con_el_formato_de_error(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_urlopen(req: Any, timeout: int) -> FakeUpstream:
        raise URLError("connection refused")

    monkeypatch.setattr(web, "urlopen", fake_urlopen)
    response = client.get("/api/v1/health")

    assert response.status_code == 502
    assert response.json is not None
    assert response.json["errors"][0]["code"] == "api_unavailable"
