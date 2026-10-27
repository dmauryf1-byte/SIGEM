from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from app.core import security
from app.modules.users import service
from app.scripts.users import run
from tests.conftest import TestSession

CREATE = ["create", "--username", "admin", "--full-name", "Ana Gómez", "--role", "Administrador"]


def prompt_with(*values: str) -> Callable[[str], str]:
    it = iter(values)
    return lambda _: next(it)


def test_create_pide_la_clave_dos_veces_y_crea(
    db: Session, capsys: pytest.CaptureFixture[str]
) -> None:
    code = run(CREATE, TestSession, prompt_with("clave-segura-123", "clave-segura-123"))

    assert code == 0
    user = service.get_by_username(db, "admin")
    assert user is not None
    assert security.verify_password(user.password_hash, "clave-segura-123")
    assert "clave-segura-123" not in capsys.readouterr().out


def test_create_rechaza_claves_distintas(db: Session) -> None:
    code = run(CREATE, TestSession, prompt_with("clave-segura-123", "otra-clave-1234"))

    assert code == 1
    assert service.get_by_username(db, "admin") is None


def test_create_rechaza_clave_corta(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(CREATE, TestSession, prompt_with("corta", "corta")) == 1
    assert "12" in capsys.readouterr().err


def test_unlock(db: Session) -> None:
    run(CREATE, TestSession, prompt_with("clave-segura-123", "clave-segura-123"))
    assert run(["unlock", "admin"], TestSession) == 0
    assert run(["unlock", "nadie"], TestSession) == 1
