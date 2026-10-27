import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings

ACCESS_TOKEN_TTL = timedelta(minutes=15)
JWT_ALGORITHM = "HS256"

_hasher = PasswordHasher()  # Argon2id con los parámetros recomendados por la librería
# Usuario inexistente: se verifica contra este hash para no revelar por tiempo si existe
DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(32))


class InvalidTokenError(Exception):
    pass


@dataclass(frozen=True)
class AccessClaims:
    user_id: int
    role: str
    session_id: str


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(*, user_id: int, role: str, session_id: str, now: datetime) -> str:
    issued = now.replace(tzinfo=UTC)
    payload = {
        "sub": str(user_id),
        "role": role,
        "sid": session_id,
        "iat": issued,
        "exp": issued + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> AccessClaims:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "role", "sid", "exp"]},
        )
        return AccessClaims(
            user_id=int(payload["sub"]), role=str(payload["role"]), session_id=str(payload["sid"])
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise InvalidTokenError from exc


def hash_refresh_token(token: str) -> str:
    # SHA-256 basta: el token es aleatorio de 256 bits, no una contraseña elegida por una persona
    return hashlib.sha256(token.encode()).hexdigest()


def new_refresh_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_refresh_token(token)
