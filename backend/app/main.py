from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core import health
from app.core.errors import AppError, app_error_handler, validation_error_handler
from app.modules.auth.router import router as auth_router

# Solo la API: las páginas las sirve Flask (web/app.py) y le reenvía /api (ADR-0004)
app = FastAPI(title="SIGEM API", version="0.1.0")
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
