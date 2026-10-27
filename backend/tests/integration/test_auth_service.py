from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.errors import AppError
from app.modules.auth import service
from app.modules.users import service as users_service
from app.modules.users.models import Role

PASSWORD = "clave-segura-123"


@pytest.fixture
def ana(db: Session) -> int:
    return users_service.create_user(
        db, username="ana", full_name="Ana Gómez", password=PASSWORD, role=Role.SELLER
    ).id


def login(db: Session, now: datetime, password: str = PASSWORD) -> service.Session:
    return service.login(db, username="ana", password=password, now=now)


def error_code(exc: pytest.ExceptionInfo[AppError]) -> tuple[int, str]:
    return exc.value.status_code, exc.value.code


@pytest.mark.usefixtures("ana")
class TestLogin:
    def test_ok_devuelve_usuario_y_tokens(self, db: Session) -> None:
        result = login(db, utcnow())

        assert result.user.username == "ana"
        assert result.access_token
        assert result.refresh_token

    def test_clave_mala_y_usuario_inexistente_dan_el_mismo_error(self, db: Session) -> None:
        with pytest.raises(AppError) as bad_password:
            login(db, utcnow(), password="clave-equivocada")
        with pytest.raises(AppError) as no_user:
            service.login(db, username="nadie", password=PASSWORD, now=utcnow())

        assert error_code(bad_password) == error_code(no_user) == (401, "invalid_credentials")
        assert bad_password.value.message == no_user.value.message

    def test_cinco_fallos_bloquean_y_a_los_15_min_vuelve_a_entrar(self, db: Session) -> None:
        now = utcnow()
        for _ in range(4):
            with pytest.raises(AppError):
                login(db, now, password="clave-equivocada")
        with pytest.raises(AppError) as fifth:
            login(db, now, password="clave-equivocada")
        assert error_code(fifth) == (423, "account_locked")

        with pytest.raises(AppError) as locked:
            login(db, now + timedelta(minutes=14), password=PASSWORD)  # ni con la clave buena
        assert error_code(locked) == (423, "account_locked")

        assert login(db, now + timedelta(minutes=15)).user.username == "ana"

    def test_usuario_inactivo_no_entra(self, db: Session) -> None:
        user = users_service.get_by_username(db, "ana")
        assert user is not None
        user.is_active = False
        db.commit()

        with pytest.raises(AppError) as exc:
            login(db, utcnow())
        assert error_code(exc) == (401, "invalid_credentials")


@pytest.mark.usefixtures("ana")
class TestRefresh:
    def test_rota_el_token_y_el_viejo_ya_no_sirve(self, db: Session) -> None:
        now = utcnow()
        first = login(db, now)

        second = service.refresh(db, first.refresh_token, now + timedelta(minutes=10))

        assert second.refresh_token != first.refresh_token
        with pytest.raises(AppError):
            service.refresh(db, first.refresh_token, now + timedelta(minutes=11))

    def test_reutilizar_un_token_usado_cierra_toda_la_sesion(self, db: Session) -> None:
        now = utcnow()
        first = login(db, now)
        second = service.refresh(db, first.refresh_token, now)

        with pytest.raises(AppError):
            service.refresh(db, first.refresh_token, now)  # alguien robó el viejo
        with pytest.raises(AppError) as exc:
            service.refresh(db, second.refresh_token, now)  # el legítimo también cae
        assert error_code(exc) == (401, "session_expired")

    def test_45_min_sin_uso_cierra_la_sesion(self, db: Session) -> None:
        now = utcnow()
        first = login(db, now)

        with pytest.raises(AppError) as exc:
            service.refresh(db, first.refresh_token, now + timedelta(minutes=45))
        assert error_code(exc) == (401, "session_expired")

    def test_un_dia_desde_el_login_cierra_aunque_haya_actividad(self, db: Session) -> None:
        start = utcnow()
        current = login(db, start)
        moment = start
        while moment < start + timedelta(hours=23, minutes=30):
            moment += timedelta(minutes=30)
            current = service.refresh(db, current.refresh_token, moment)

        with pytest.raises(AppError) as exc:
            service.refresh(db, current.refresh_token, start + timedelta(days=1))
        assert error_code(exc) == (401, "session_expired")

    def test_token_desconocido(self, db: Session) -> None:
        with pytest.raises(AppError) as exc:
            service.refresh(db, "inventado", utcnow())
        assert error_code(exc) == (401, "session_expired")


@pytest.mark.usefixtures("ana")
def test_logout_revoca_la_sesion(db: Session) -> None:
    now = utcnow()
    session = login(db, now)

    service.logout(db, session.refresh_token, now)

    with pytest.raises(AppError):
        service.refresh(db, session.refresh_token, now)


@pytest.mark.usefixtures("ana")
def test_reset_password_cambia_clave_desbloquea_y_cierra_sesiones(db: Session) -> None:
    now = utcnow()
    open_session = login(db, now)
    for _ in range(5):
        with pytest.raises(AppError):
            login(db, now, password="clave-equivocada")

    service.reset_password(db, "ana", "clave-nueva-456", now)

    with pytest.raises(AppError):
        service.refresh(db, open_session.refresh_token, now)
    with pytest.raises(AppError):
        login(db, now, password=PASSWORD)
    assert login(db, now, password="clave-nueva-456").user.username == "ana"


def test_intentos_simultaneos_no_esquivan_el_bloqueo(ana: int) -> None:
    """Hallazgo de security-guidance: sin FOR UPDATE los fallos en paralelo se pisan."""
    from concurrent.futures import ThreadPoolExecutor

    from tests.conftest import TestSession

    now = utcnow()

    def wrong_login(_: int) -> int:
        with TestSession() as db:
            try:
                service.login(db, username="ana", password="clave-equivocada", now=now)
            except AppError as exc:
                return exc.status_code
        return 200

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(wrong_login, range(10)))

    assert codes.count(401) == 4  # exactamente 4 fallos "normales"; del 5.º en adelante, bloqueo
    assert codes.count(423) == 6
