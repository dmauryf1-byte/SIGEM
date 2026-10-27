from pathlib import PurePath

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Scope

from app.core import health

FRONTEND_DIR = PurePath(__file__).parents[2] / "frontend"
PUBLIC_DIRS = {"css", "js"}


class FrontendFiles(StaticFiles):
    """Sirve solo lo que usa el navegador: las páginas .html de la raíz, css/ y js/.

    frontend/ también tiene node_modules, tests y configuración de desarrollo, que no se publican.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        parts = PurePath(path).parts
        is_page = len(parts) <= 1 and (not parts or parts[0] == "." or path.endswith(".html"))
        if not (is_page or parts[0] in PUBLIC_DIRS):
            raise HTTPException(status_code=404)
        return await super().get_response(path, scope)


app = FastAPI(title="SIGEM API", version="0.1.0")
app.include_router(health.router, prefix="/api/v1")
# Va al final: un montaje en "/" atrapa todo lo que no resolvieron las rutas anteriores
app.mount("/", FrontendFiles(directory=FRONTEND_DIR, html=True), name="frontend")
