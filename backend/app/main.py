from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core import health

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="SIGEM API", version="0.1.0")
app.include_router(health.router, prefix="/api/v1")
# Va al final: un montaje en "/" atrapa todo lo que no resolvieron las rutas anteriores
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
