from fastapi import FastAPI

from app.core import health

app = FastAPI(title="SIGEM API", version="0.1.0")
app.include_router(health.router, prefix="/api/v1")
