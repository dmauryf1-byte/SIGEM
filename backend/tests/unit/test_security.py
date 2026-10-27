from datetime import timedelta

import jwt
import pytest

from app.core import security
from app.core.clock import utcnow


def test_hash_y_verificacion_argon2() -> None:
    hashed = security.hash_password("una clave larga y segura")

    assert hashed.startswith("$argon2id$")
    assert "una clave" not in hashed
    assert security.verify_password(hashed, "una clave larga y segura")
    assert not security.verify_password(hashed, "otra clave cualquiera")


def test_verificar_contra_hash_invalido_no_lanza() -> None:
    assert not security.verify_password("no-es-un-hash", "lo que sea")


def test_hash_senuelo_nunca_coincide() -> None:
    assert not security.verify_password(security.DUMMY_HASH, "")


def test_token_de_acceso_ida_y_vuelta() -> None:
    token = security.create_access_token(user_id=7, role="Vendedor", session_id="s1", now=utcnow())

    claims = security.decode_access_token(token)

    assert claims.user_id == 7
    assert claims.role == "Vendedor"
    assert claims.session_id == "s1"


def test_token_de_acceso_vencido_se_rechaza() -> None:
    past = utcnow() - security.ACCESS_TOKEN_TTL - timedelta(seconds=1)
    token = security.create_access_token(user_id=7, role="Vendedor", session_id="s1", now=past)

    with pytest.raises(security.InvalidTokenError):
        security.decode_access_token(token)


def test_token_de_acceso_alterado_se_rechaza() -> None:
    forged = jwt.encode(
        {"sub": "1", "role": "Administrador"},
        "otra-clave-de-al-menos-32-bytes-de-largo",
        algorithm="HS256",
    )

    with pytest.raises(security.InvalidTokenError):
        security.decode_access_token(forged)


def test_token_sin_algoritmo_se_rechaza() -> None:
    unsigned = jwt.encode({"sub": "1", "role": "Administrador"}, None, algorithm="none")

    with pytest.raises(security.InvalidTokenError):
        security.decode_access_token(unsigned)


def test_token_de_renovacion_aleatorio_y_guardado_como_hash() -> None:
    token, token_hash = security.new_refresh_token()
    other, _ = security.new_refresh_token()

    assert token != other
    assert len(token) >= 40
    assert token_hash == security.hash_refresh_token(token)
    assert token not in token_hash
