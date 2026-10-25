from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.db import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: Annotated[Session, Depends(get_session)]) -> JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse(
            status_code=503,
            content={
                "errors": [
                    {
                        "field": None,
                        "code": "database_unavailable",
                        "message": "La base de datos no responde",
                    }
                ]
            },
        )
    return JSONResponse(content={"status": "ok", "database": "ok"})
