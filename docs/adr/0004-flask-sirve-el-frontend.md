# ADR-0004 — Flask sirve el frontend

- **Estado:** aceptado por el humano el 2026-11-17
- **Cambia en AGENTS.md §1:** "FastAPI (también sirve `frontend/` como estáticos)" → Flask sirve las páginas; FastAPI queda solo como API.
- **Cambia en ADR-0001:** la fila "Servidor web".

## Contexto

El humano pidió que el frontend (HTML + CSS + JavaScript) se ejecute con **Python y Flask**, para trabajarlo en Visual Studio Code como parte de su trabajo académico. El backend de FastAPI ya tiene el login con JWT en cookies `HttpOnly`, el RBAC y sus tests (SIGEM-004), y las tablas del negocio (SIGEM-018).

Opciones que se le presentaron:

1. **Flask sirve el frontend y reenvía `/api` a FastAPI** (elegida).
2. Reescribir todo el backend en Flask: rehacer auth, JWT, usuarios y sus tests.
3. Una app Flask aparte, solo visual, sin conexión a la base de datos.

## Decisión

- `web/app.py` (Flask) sirve las páginas `.html` de `frontend/` (lista cerrada `PAGES`), `css/` y `js/`. Nada más de `frontend/` se publica (`package.json`, `node_modules/`, `tests/`).
- Flask reenvía `/api/*` a FastAPI (`SIGEM_API_URL`, por defecto `http://127.0.0.1:8000`) con `urllib` de la biblioteca estándar, incluidas las cookies en ambos sentidos. El navegador sigue viendo **un solo origen** (sin CORS) y las cookies `SameSite=Strict` siguen funcionando.
- FastAPI deja de montar `frontend/`: solo atiende `/api/v1`.
- Las páginas siguen siendo HTML estático, sin plantillas Jinja: no cambia nada de ADR-0001 salvo quién las entrega.
- Proyecto propio con uv en `web/` (dependencia: `flask`; desarrollo: pytest, ruff, mypy).

## Consecuencias

- **A favor:** se cumple el pedido del humano sin perder SIGEM-004 ni sus tests; las reglas de §3 y §4 de AGENTS.md no cambian (la lógica sigue en FastAPI).
- **En contra:** hay que levantar dos procesos en desarrollo (FastAPI en 8000 y Flask en 5000) y cada llamada a la API da un salto más. Para una app interna de una microempresa el costo es despreciable.
- Playwright arranca ambos servidores y entra por Flask (`baseURL` 5000).
- Si un día se despliega con un proxy (Nginx, Caddy), ese proxy puede reemplazar el reenvío de Flask sin tocar el frontend.
