# SIGEM-002 — Estructura del backend y prueba real FastAPI → MySQL

- **Estado:** borrador, pendiente de aprobación del humano
- **Rama:** `feat/SIGEM-002-estructura-backend`
- **Bloquea a:** todos los módulos de negocio (AGENTS.md §8)

## Objetivo

Dejar el esqueleto del backend listo para que el primer módulo de negocio (`customers` u otro) solo tenga que agregar sus archivos, sin decidir nada de infraestructura.

El éxito se demuestra con **una petición real**: `GET /api/v1/health` responde `200` porque FastAPI consultó a MySQL 8.4 corriendo en Docker, y responde `503` cuando MySQL no está disponible. Ambos casos tienen test.

### Fuera de alcance
- Frontend: va en **SIGEM-003** (Vite + React + TS strict).
- Módulos de negocio, tablas y migraciones con contenido.
- Autenticación (JWT/RBAC): fase 6.
- Dockerfile del backend y CI: fases 16–17.

## Decisiones (aprobadas por el humano el 2026-10-07)

| Decisión | Elegido | Descartado y por qué |
|---|---|---|
| Alcance | Solo backend + MySQL; frontend en SIGEM-003 | Todo junto: PR demasiado grande para revisar |
| Ejecución en desarrollo | Backend local con `uv`; Docker Compose solo levanta MySQL | Todo en Docker: recarga y depuración lentas en Windows |
| ORM | SQLAlchemy 2.x **síncrono** + **PyMySQL** | Async + asyncmy: más complejidad en sesiones y tests sin necesidad medida. `with_for_update()` funciona igual en síncrono |

La decisión síncrono vs. asíncrono es costosa de revertir, así que se registra como `docs/adr/0001-sqlalchemy-sincrono.md`.

## Stack de esta tarea

| Pieza | Versión / detalle |
|---|---|
| Python | 3.12 (fijado en `backend/.python-version`; `requires-python = ">=3.12"`) |
| Dependencias | `fastapi[standard]`, `sqlalchemy>=2`, `pymysql`, `cryptography` (requerida por PyMySQL para `caching_sha2_password`, el método de autenticación por defecto de MySQL 8.4), `alembic`, `pydantic-settings` |
| Dependencias dev | `pytest`, `pytest-cov`, `httpx`, `ruff`, `mypy` |
| Base de datos | imagen `mysql:8.4`, `utf8mb4` |

## Comandos

```powershell
# Base de datos (desde la raíz del repo)
Copy-Item .env.example .env          # una sola vez; editar contraseñas
docker compose up -d mysql
docker compose ps                    # mysql debe quedar "healthy"

# Backend
cd backend
uv sync
uv run fastapi dev app/main.py       # http://localhost:8000/api/v1/health  y  /docs

# Verificación (AGENTS.md §7)
uv run ruff check . ; uv run ruff format --check . ; uv run mypy app ; uv run pytest --cov=app
```

## Estructura

```
.env.example                 # variables de MySQL y del backend (sin secretos reales)
docker-compose.yml           # servicio mysql:8.4 con healthcheck y volumen
docker/mysql/init/01-test-db.sql   # crea la base sigem_test y da permisos al usuario de la app
backend/
  .python-version
  pyproject.toml             # dependencias + config de ruff, mypy (strict) y pytest
  uv.lock
  alembic.ini
  alembic/env.py             # toma la URL de core/config.py; sin migraciones todavía
  alembic/versions/          # vacío (.gitkeep)
  app/
    __init__.py
    main.py                  # crea la app e incluye routers bajo /api/v1
    core/
      __init__.py
      config.py              # Settings (pydantic-settings) leídas de .env
      db.py                  # engine, SessionLocal, dependencia get_session
      health.py              # router GET /api/v1/health
    modules/
      __init__.py            # vacío: cada módulo de negocio llega con su tarea
  tests/
    conftest.py              # cliente httpx contra la app y base sigem_test
    integration/test_health.py
```

`health.py` vive en `core/` porque es infraestructura, no un módulo de negocio. Por eso no tiene `service`/`repository`.

## Estilo de código

```python
# app/core/health.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.db import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: Session = Depends(get_session)) -> JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse(
            status_code=503,
            content={"errors": [{"field": None, "code": "database_unavailable",
                                 "message": "La base de datos no responde"}]},
        )
    return JSONResponse(content={"status": "ok", "database": "ok"})
```

- Type hints completos; `mypy --strict` sin `# type: ignore`.
- `ruff` formatea y ordena imports; longitud de línea 100.
- Mensajes al usuario en español; nombres de código y rutas en inglés (AGENTS.md §4).
- Errores siempre con el formato único `{"errors": [...]}` (AGENTS.md §4), incluido el `503`.

## Estrategia de tests

| Nivel | Qué cubre | Dónde |
|---|---|---|
| Integración | `GET /api/v1/health` → `200` contra MySQL real (base `sigem_test`) | `tests/integration/test_health.py` |
| Integración | `GET /api/v1/health` → `503` con el formato de error cuando la BD no responde (se sobreescribe `get_session` con un engine apuntando a un puerto cerrado) | mismo archivo |

- Los tests usan **MySQL real**, nunca SQLite. El test de concurrencia de stock de AGENTS.md §3.2 lo exigirá más adelante y la infraestructura queda lista desde ahora.
- Si MySQL no está levantado, el test de `200` **falla** con un mensaje claro (`docker compose up -d mysql`); no se marca como `skip`.
- Cobertura: todavía no hay `service.py`. La meta de 80 % aplica desde el primer módulo.

## Límites

- **Siempre:** ejecutar los comandos de AGENTS.md §7 antes de cada commit; mantener `.env.example` al día; usar el formato de error único.
- **Preguntar antes:** agregar dependencias fuera de la lista de arriba; cambiar puertos o versiones de imagen; crear tablas.
- **Nunca:** subir `.env` o contraseñas; usar SQLite en tests; crear carpetas de módulos vacías "para después".

## Criterios de aceptación

1. `docker compose up -d mysql` deja el contenedor `healthy` y existen las bases `sigem` y `sigem_test`, ambas con `utf8mb4`.
2. Con MySQL arriba, `uv run fastapi dev app/main.py` sirve `GET /api/v1/health` → `200 {"status":"ok","database":"ok"}`.
3. Con MySQL detenido (`docker compose stop mysql`), el mismo endpoint → `503` con `{"errors":[{"code":"database_unavailable", ...}]}`, sin traza de error expuesta.
4. `uv run alembic current` se conecta a MySQL sin error (no hay migraciones todavía).
5. `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app` y `uv run pytest --cov=app` en verde; la salida se pega en el PR.
6. `.env` no está en Git; `.env.example` contiene todas las variables usadas.
7. `docs/adr/0001-sqlalchemy-sincrono.md` registra la decisión del ORM.
8. `codebase-memory-mcp` indexa el repo (`index_repository`), como indica CLAUDE.md §3.
9. `AGENTS.md` §8 se actualiza: SIGEM-002 completada; siguiente, SIGEM-003.

## Preguntas abiertas

- Ninguna. El puerto `3306` está libre porque no hay MySQL local instalado. Si algún día choca, se cambia solo el mapeo de `docker-compose.yml`.
