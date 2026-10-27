from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import RefreshToken


def get_by_hash_for_update(session: Session, token_hash: str) -> RefreshToken | None:
    # FOR UPDATE: dos renovaciones simultáneas con el mismo token no pueden rotarlo las dos
    return session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash).with_for_update()
    )


def add(session: Session, token: RefreshToken) -> None:
    session.add(token)
    session.flush()


def revoke_session(session: Session, session_id: str, now: datetime) -> None:
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.session_id == session_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )


def revoke_user(session: Session, user_id: int, now: datetime) -> None:
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
