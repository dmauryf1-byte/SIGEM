"""Login, renovación y cierre de sesión (SIGEM-004).

Sesión = JWT de acceso (15 min) + token de renovación opaco que dura 45 min y se rota en cada uso.
Ninguna sesión pasa de 1 día desde el login.
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session as DbSession

from app.core import security
from app.core.errors import AppError
from app.modules.auth import repository
from app.modules.auth.models import RefreshToken
from app.modules.users import service as users_service
from app.modules.users.models import User

REFRESH_IDLE_TTL = timedelta(minutes=45)
SESSION_MAX_AGE = timedelta(days=1)


@dataclass(frozen=True)
class Session:
    user: User
    access_token: str
    refresh_token: str
    refresh_expires_at: datetime


def _invalid_credentials() -> AppError:
    return AppError(401, "invalid_credentials", "Usuario o contraseña incorrectos")


def _account_locked() -> AppError:
    return AppError(
        423,
        "account_locked",
        "Cuenta bloqueada temporalmente. Intenta de nuevo en 15 minutos o pide al "
        "administrador que la desbloquee.",
    )


def _session_expired() -> AppError:
    return AppError(401, "session_expired", "La sesión terminó. Inicia sesión de nuevo")


def _issue(
    db: DbSession, user: User, session_id: str, started_at: datetime, now: datetime
) -> Session:
    token, token_hash = security.new_refresh_token()
    expires_at = min(now + REFRESH_IDLE_TTL, started_at + SESSION_MAX_AGE)
    repository.add(
        db,
        RefreshToken(
            user_id=user.id,
            session_id=session_id,
            token_hash=token_hash,
            session_started_at=started_at,
            expires_at=expires_at,
        ),
    )
    access = security.create_access_token(user_id=user.id, role=user.role.value, now=now)
    return Session(
        user=user, access_token=access, refresh_token=token, refresh_expires_at=expires_at
    )


def login(db: DbSession, *, username: str, password: str, now: datetime) -> Session:
    user = users_service.get_by_username(db, username)
    if user is None:
        security.verify_password(security.DUMMY_HASH, password)  # mismo tiempo que un usuario real
        raise _invalid_credentials()
    if users_service.is_locked(user, now):
        raise _account_locked()
    if not security.verify_password(user.password_hash, password):
        users_service.register_failed_login(user, now)
        db.commit()
        raise _account_locked() if users_service.is_locked(user, now) else _invalid_credentials()
    if not user.is_active:
        raise _invalid_credentials()

    users_service.register_successful_login(user)
    result = _issue(db, user, secrets.token_urlsafe(32), now, now)
    db.commit()
    return result


def refresh(db: DbSession, token: str, now: datetime) -> Session:
    stored = repository.get_by_hash_for_update(db, security.hash_refresh_token(token))
    if stored is None:
        raise _session_expired()
    if stored.revoked_at is not None:
        # Un token ya usado vuelve a aparecer: puede ser robado, se cierra toda la sesión
        repository.revoke_session(db, stored.session_id, now)
        db.commit()
        raise _session_expired()
    user = users_service.get_by_id(db, stored.user_id)
    if (
        now >= stored.expires_at
        or now >= stored.session_started_at + SESSION_MAX_AGE
        or user is None
        or not user.is_active
    ):
        db.rollback()
        raise _session_expired()

    stored.revoked_at = now
    result = _issue(db, user, stored.session_id, stored.session_started_at, now)
    db.commit()
    return result


def logout(db: DbSession, token: str, now: datetime) -> None:
    stored = repository.get_by_hash_for_update(db, security.hash_refresh_token(token))
    if stored is not None:
        repository.revoke_session(db, stored.session_id, now)
    db.commit()


def reset_password(db: DbSession, username: str, new_password: str, now: datetime) -> User:
    user = users_service.change_password(db, username, new_password)
    repository.revoke_user(db, user.id, now)
    db.commit()
    return user
