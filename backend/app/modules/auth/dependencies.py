from collections.abc import Callable
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core import security
from app.core.db import get_session
from app.core.errors import AppError
from app.modules.users import service as users_service
from app.modules.users.models import Role, User

ACCESS_COOKIE = "sigem_access"


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    sigem_access: Annotated[str | None, Cookie()] = None,
) -> User:
    not_authenticated = AppError(401, "not_authenticated", "Inicia sesión para continuar")
    if not sigem_access:
        raise not_authenticated
    try:
        claims = security.decode_access_token(sigem_access)
    except security.InvalidTokenError as exc:
        raise not_authenticated from exc
    # El rol y el estado salen de la BD, no del token: un usuario desactivado pierde acceso ya
    user = users_service.get_by_id(session, claims.user_id)
    if user is None or not user.is_active:
        raise not_authenticated
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: Role) -> Callable[[User], User]:
    def check(user: CurrentUser) -> User:
        if user.role not in roles:
            raise AppError(403, "forbidden", "No tienes permiso para esta acción")
        return user

    return check
