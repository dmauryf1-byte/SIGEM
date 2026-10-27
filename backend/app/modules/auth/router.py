from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.core import security
from app.core.clock import utcnow
from app.core.config import settings
from app.core.db import get_session
from app.core.errors import AppError
from app.modules.auth import service
from app.modules.auth.dependencies import ACCESS_COOKIE, CurrentUser
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "sigem_refresh"
ACCESS_PATH = "/api"
REFRESH_PATH = "/api/v1/auth"

DbSession = Annotated[Session, Depends(get_session)]
RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE)]


def _set_cookie(response: Response, name: str, value: str, max_age: int, path: str) -> None:
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        path=path,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
    )


def _set_cookies(response: Response, session: service.Session) -> None:
    access_ttl = int(security.ACCESS_TOKEN_TTL.total_seconds())
    refresh_ttl = int((session.refresh_expires_at - utcnow()).total_seconds())
    _set_cookie(response, ACCESS_COOKIE, session.access_token, access_ttl, ACCESS_PATH)
    _set_cookie(response, REFRESH_COOKIE, session.refresh_token, refresh_ttl, REFRESH_PATH)


def _clear_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path=ACCESS_PATH)
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_PATH)


@router.post("/login")
def login(body: LoginRequest, db: DbSession, response: Response) -> LoginResponse:
    session = service.login(db, username=body.username, password=body.password, now=utcnow())
    _set_cookies(response, session)
    return LoginResponse(user=UserOut.model_validate(session.user))


@router.post("/refresh")
def refresh(db: DbSession, response: Response, token: RefreshCookie = None) -> LoginResponse:
    try:
        session = service.refresh(db, token or "", utcnow())
    except AppError:
        _clear_cookies(response)
        raise
    _set_cookies(response, session)
    return LoginResponse(user=UserOut.model_validate(session.user))


@router.post("/logout", status_code=204)
def logout(db: DbSession, response: Response, token: RefreshCookie = None) -> None:
    if token:
        service.logout(db, token, utcnow())
    _clear_cookies(response)


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
