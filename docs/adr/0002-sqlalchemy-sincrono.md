# ADR-0002 — SQLAlchemy síncrono con PyMySQL

- **Estado:** aceptado por el humano el 2026-10-07 (spec SIGEM-002)

## Contexto

FastAPI admite rutas síncronas y asíncronas. Con SQLAlchemy 2.x hay dos caminos: motor síncrono (PyMySQL) o asíncrono (asyncmy/aiomysql). Cambiar de uno a otro después obliga a reescribir sesiones, repositorios y tests, así que se decide una vez.

## Decisión

SQLAlchemy 2.x **síncrono** con el driver **PyMySQL** (+ `cryptography` para la autenticación `caching_sha2_password` de MySQL 8.4). Las rutas que usan la BD son `def`, no `async def`: FastAPI las ejecuta en su pool de hilos.

## Consecuencias

- Sesiones y tests más simples (`with SessionLocal() as session`), sin `await` en cada capa.
- `with_for_update()` (AGENTS.md §3.2) funciona igual que en asíncrono.
- Para una microempresa (pocos usuarios simultáneos) el pool de hilos alcanza de sobra. Si una medición muestra lo contrario, se reabre esta decisión.
- Descartado: asíncrono + asyncmy, por más complejidad sin necesidad medida.
