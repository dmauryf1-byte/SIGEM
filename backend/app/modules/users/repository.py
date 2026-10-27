from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models import User


def get_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_by_username(session: Session, username: str) -> User | None:
    return session.scalar(select(User).where(User.username == username))


def get_by_username_for_update(session: Session, username: str) -> User | None:
    # FOR UPDATE: intentos de login simultáneos no pueden pisarse el contador de fallos
    return session.scalar(select(User).where(User.username == username).with_for_update())


def add(session: Session, user: User) -> None:
    session.add(user)
    session.flush()
