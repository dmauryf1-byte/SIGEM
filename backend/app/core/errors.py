from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Error de negocio con el formato único de AGENTS.md §4."""

    def __init__(self, status_code: int, code: str, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field = field


def error_body(code: str, message: str, field: str | None = None) -> dict[str, object]:
    return {"errors": [{"field": field, "code": code, "message": message}]}


async def app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppError):  # FastAPI solo lo registra para AppError
        raise exc
    return JSONResponse(
        status_code=exc.status_code, content=error_body(exc.code, exc.message, exc.field)
    )
