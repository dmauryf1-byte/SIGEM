"""Servidor web de SIGEM hecho con Flask (ADR-0004).

Qué hace este archivo:
1. Muestra las pantallas (archivos .html de la carpeta frontend/).
2. Entrega los estilos (css/) y el código JavaScript (js/).
3. Pasa las llamadas /api/... al backend de FastAPI, que es quien habla con MySQL.

Cómo se ejecuta:  cd web  y luego  uv run flask --app app run --port 5000
"""

import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, Response, abort, jsonify, request, send_from_directory

# ─── Configuración ────────────────────────────────────────────────────────────
# Carpetas del frontend (frontend/ queda al lado de web/): cada lenguaje en la suya
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
HTML_DIR = FRONTEND_DIR / "html"  # pantallas
CSS_DIR = FRONTEND_DIR / "css"  # estilos
JS_DIR = FRONTEND_DIR / "js"  # código JavaScript

# Dirección del backend de FastAPI. Se puede cambiar con la variable SIGEM_API_URL
API_URL = os.environ.get("SIGEM_API_URL", "http://127.0.0.1:8000")

# Lista de pantallas que se pueden abrir. Si una página no está aquí, Flask responde 404.
# Así no se publican por error archivos de desarrollo como package.json o node_modules.
PAGES = {
    "index",  # login
    "dashboard",
    "clientes",
    "productos",
    "vendedores",
    "proveedores",
    "facturas",
    "factura-nueva",
    "pagos",
    "reportes",
    "usuarios",
}

# Encabezados que se copian de la petición del navegador hacia FastAPI
FORWARDED_HEADERS = ("Content-Type", "Cookie", "Accept")

# static_folder=None: los archivos estáticos los entregamos nosotros con las rutas de abajo
app = Flask(__name__, static_folder=None)


# ─── Pantallas (HTML) ─────────────────────────────────────────────────────────
@app.get("/")
def home() -> Response:
    # La raíz del sitio muestra el login
    return send_from_directory(HTML_DIR, "index.html")


@app.get("/<page>.html")
def page(page: str) -> Response:
    # Si la página no está en la lista PAGES, respondemos "no encontrada"
    if page not in PAGES:
        abort(404)
    return send_from_directory(HTML_DIR, f"{page}.html")


# ─── Estilos y JavaScript ─────────────────────────────────────────────────────
@app.get("/css/<path:filename>")
def css(filename: str) -> Response:
    # send_from_directory no deja salir de la carpeta (bloquea rutas como ../../)
    return send_from_directory(CSS_DIR, filename)


@app.get("/js/<path:filename>")
def js(filename: str) -> Response:
    return send_from_directory(JS_DIR, filename)


# ─── Puente hacia la API de FastAPI ───────────────────────────────────────────
@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def api(path: str) -> Response | tuple[Response, int]:
    # 1. Armamos la misma petición, pero dirigida al backend
    url = f"{API_URL}/api/{path}"
    if request.query_string:
        url += "?" + request.query_string.decode()
    headers = {name: value for name in FORWARDED_HEADERS if (value := request.headers.get(name))}
    upstream_request = Request(  # noqa: S310 - la URL base es fija (API_URL), no la elige el usuario
        url, data=request.get_data() or None, headers=headers, method=request.method
    )

    # 2. La enviamos. Un 401 o 422 de FastAPI llega como HTTPError, pero es una respuesta normal
    try:
        with urlopen(upstream_request, timeout=15) as upstream:  # noqa: S310 - misma razón
            status, upstream_headers, body = upstream.status, upstream.headers, upstream.read()
    except HTTPError as error:
        status, upstream_headers, body = error.code, error.headers, error.read()
    except URLError:
        # El backend está apagado: respondemos con el formato de error de AGENTS.md §4
        message = "No se pudo conectar con el servidor de SIGEM. Intenta de nuevo."
        error_body = {"errors": [{"field": None, "code": "api_unavailable", "message": message}]}
        return jsonify(error_body), 502

    # 3. Devolvemos al navegador lo mismo que respondió FastAPI, incluidas las cookies de sesión
    response = Response(body, status=status, content_type=upstream_headers.get("Content-Type"))
    for cookie in upstream_headers.get_all("Set-Cookie") or []:
        response.headers.add("Set-Cookie", cookie)
    return response
