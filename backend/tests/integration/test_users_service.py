from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.core import security
from app.core.clock import utcnow
from app.core.errors import AppError
from app.modules.users import service
from app.modules.users.models import Role

PASSWORD = "clave-de-doce"  # 13 caracteres


def create(db: Session, username: str = "ana", role: Role = Role.SELLER) -> int:
    return service.create_user(
        db, username=username, full_name="Ana Gómez", password=PASSWORD, role=role
    ).id


def test_crear_usuario_guarda_hash_y_no_la_clave(db: Session) -> None:
    user = service.create_user(
        db, username=" ana ", full_name="Ana Gómez", password=PASSWORD, role=Role.ADMIN
    )

    assert user.username == "ana"
    assert user.role is Role.ADMIN
    assert user.is_active
    assert user.password_hash != PASSWORD
    assert security.verify_password(user.password_hash, PASSWORD)


@pytest.mark.parametrize("password", ["once-chars!", "x" * 129])
def test_politica_de_longitud(db: Session, password: str) -> None:
    with pytest.raises(AppError) as exc:
        service.create_user(
            db, username="ana", full_name="Ana", password=password, role=Role.SELLER
        )
    assert exc.value.code == "password_length"


def test_doce_caracteres_es_el_minimo(db: Session) -> None:
    service.create_user(db, username="ana", full_name="Ana", password="x" * 12, role=Role.SELLER)


def test_usuario_repetido_sin_distinguir_mayusculas(db: Session) -> None:
    create(db, "ana")
    with pytest.raises(AppError) as exc:
        create(db, "ANA")
    assert exc.value.code == "username_taken"


def test_cinco_fallos_bloquean_quince_minutos(db: Session) -> None:
    user = service.get_by_id(db, create(db))
    assert user is not None
    now = utcnow()

    for _ in range(4):
        service.register_failed_login(user, now)
    assert not service.is_locked(user, now)

    service.register_failed_login(user, now)
    assert service.is_locked(user, now)
    assert service.is_locked(user, now + timedelta(minutes=14, seconds=59))
    assert not service.is_locked(user, now + timedelta(minutes=15))


def test_login_correcto_reinicia_el_contador(db: Session) -> None:
    user = service.get_by_id(db, create(db))
    assert user is not None
    for _ in range(4):
        service.register_failed_login(user, utcnow())

    service.register_successful_login(user)

    assert user.failed_login_attempts == 0
    assert user.locked_until is None


def test_unlock_desbloquea_al_momento(db: Session) -> None:
    user_id = create(db)
    user = service.get_by_id(db, user_id)
    assert user is not None
    for _ in range(5):
        service.register_failed_login(user, utcnow())
    db.commit()

    service.unlock_user(db, "ana")

    db.expire_all()
    refreshed = service.get_by_id(db, user_id)
    assert refreshed is not None
    assert not service.is_locked(refreshed, utcnow())
    assert refreshed.failed_login_attempts == 0


def test_unlock_de_usuario_inexistente(db: Session) -> None:
    with pytest.raises(AppError) as exc:
        service.unlock_user(db, "nadie")
    assert exc.value.code == "user_not_found"
