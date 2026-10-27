from collections.abc import Callable

import httpx
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.modules.auth.dependencies import require_role
from app.modules.users import service as users_service
from app.modules.users.models import Role

PASSWORD = "clave-segura-123"


@app.get("/api/v1/_test/admin-only", dependencies=[Depends(require_role(Role.ADMIN))])
def admin_only() -> dict[str, str]:
    return {"ok": "yes"}


# El montaje del frontend en "/" atrapa todo lo registrado después: la ruta de prueba va primero
app.router.routes.insert(0, app.router.routes.pop())


@pytest.fixture
def make_user(db: Session) -> Callable[[str, Role], None]:
    def make(username: str, role: Role) -> None:
        users_service.create_user(
            db, username=username, full_name="Ana Gómez", password=PASSWORD, role=role
        )

    return make


def do_login(client: TestClient, username: str = "ana", password: str = PASSWORD) -> httpx.Response:
    return client.post("/api/v1/auth/login", json={"username": username, "password": password})


def test_login_pone_cookies_httponly_y_samesite_strict(
    client: TestClient, make_user: Callable[[str, Role], None]
) -> None:
    make_user("ana", Role.SELLER)

    response = do_login(client)

    assert response.status_code == 200
    assert response.json()["user"] == {
        "id": response.json()["user"]["id"],
        "username": "ana",
        "full_name": "Ana Gómez",
        "role": "Vendedor",
    }
    cookies = response.headers.get_list("set-cookie")
    access = next(c for c in cookies if c.startswith("sigem_access="))
    refresh = next(c for c in cookies if c.startswith("sigem_refresh="))
    for cookie in (access, refresh):
        assert "HttpOnly" in cookie
        assert "SameSite=strict" in cookie
    assert "Path=/api;" in access
    assert "Path=/api/v1/auth" in refresh
    assert "token" not in response.text.lower()


def test_login_malo_formato_de_error_unico(client: TestClient) -> None:
    response = do_login(client, "nadie")

    assert response.status_code == 401
    assert response.json() == {
        "errors": [
            {
                "field": None,
                "code": "invalid_credentials",
                "message": "Usuario o contraseña incorrectos",
            }
        ]
    }


def test_login_sin_campos_da_422_con_formato_unico(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"username": ""})

    assert response.status_code == 422
    fields = {e["field"] for e in response.json()["errors"]}
    assert fields == {"username", "password"}


def test_me_sin_sesion_da_401(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "not_authenticated"


def test_me_con_token_falso_da_401(client: TestClient) -> None:
    client.cookies.set("sigem_access", "falso", path="/api")
    assert client.get("/api/v1/auth/me").status_code == 401


def test_flujo_login_me_refresh_logout(
    client: TestClient, make_user: Callable[[str, Role], None]
) -> None:
    make_user("ana", Role.SELLER)
    do_login(client)

    assert client.get("/api/v1/auth/me").json()["username"] == "ana"

    old_refresh = client.cookies.get("sigem_refresh")
    assert client.post("/api/v1/auth/refresh").status_code == 200
    assert client.cookies.get("sigem_refresh") != old_refresh

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.post("/api/v1/auth/refresh").status_code == 401

    client.cookies.set("sigem_refresh", old_refresh or "", path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_usuario_desactivado_pierde_acceso_aunque_tenga_token(
    client: TestClient, make_user: Callable[[str, Role], None], db: Session
) -> None:
    make_user("ana", Role.SELLER)
    do_login(client)
    user = users_service.get_by_username(db, "ana")
    assert user is not None
    user.is_active = False
    db.commit()

    assert client.get("/api/v1/auth/me").status_code == 401


def test_require_role(client: TestClient, make_user: Callable[[str, Role], None]) -> None:
    make_user("ana", Role.SELLER)
    make_user("jefe", Role.ADMIN)

    assert client.get("/api/v1/_test/admin-only").status_code == 401
    do_login(client, "ana")
    seller = client.get("/api/v1/_test/admin-only")
    assert seller.status_code == 403
    assert seller.json()["errors"][0]["code"] == "forbidden"

    do_login(client, "jefe")
    assert client.get("/api/v1/_test/admin-only").status_code == 200
