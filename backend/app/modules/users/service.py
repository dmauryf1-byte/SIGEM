"""Usuarios: alta, política de contraseña y bloqueo por intentos (OWASP).

Las funciones que solo cambian el estado del usuario (register_*, change_password) no hacen commit:
las usa auth.service dentro de su propia transacción.
"""

from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.errors import AppError
from app.modules.users import repository
from app.modules.users.models import Role, User

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128  # Argon2 con entradas enormes se vuelve un vector de DoS
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def _validate_password(password: str) -> None:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise AppError(
            422,
            "password_length",
            f"La contraseña debe tener entre {MIN_PASSWORD_LENGTH} y {MAX_PASSWORD_LENGTH} "
            "caracteres",
            field="password",
        )


def _user_not_found() -> AppError:
    return AppError(404, "user_not_found", "El usuario no existe", field="username")


def get_by_id(session: Session, user_id: int) -> User | None:
    return repository.get_by_id(session, user_id)


def get_by_username(session: Session, username: str) -> User | None:
    return repository.get_by_username(session, username.strip())


def create_user(
    session: Session, *, username: str, full_name: str, password: str, role: Role
) -> User:
    _validate_password(password)
    user = User(
        username=username.strip(),
        full_name=full_name.strip(),
        password_hash=security.hash_password(password),
        role=role,
    )
    try:
        repository.add(session, user)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise AppError(
            409, "username_taken", "Ese nombre de usuario ya existe", field="username"
        ) from exc
    return user


def is_locked(user: User, now: datetime) -> bool:
    return user.locked_until is not None and now < user.locked_until


def register_failed_login(user: User, now: datetime) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = now + LOCKOUT_DURATION
        user.failed_login_attempts = 0


def register_successful_login(user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None


def change_password(session: Session, username: str, new_password: str) -> User:
    """Cambia la contraseña y desbloquea. Sin commit: auth.service también cierra las sesiones."""
    _validate_password(new_password)
    user = get_by_username(session, username)
    if user is None:
        raise _user_not_found()
    user.password_hash = security.hash_password(new_password)
    register_successful_login(user)
    return user


def unlock_user(session: Session, username: str) -> User:
    user = get_by_username(session, username)
    if user is None:
        raise _user_not_found()
    register_successful_login(user)
    session.commit()
    return user
