# ADR-0003 — Modelo de datos en español, del diagrama del humano

- **Estado:** aceptado por el humano el 2026-11-16 (spec SIGEM-018)

## Contexto

El plan creaba las tablas de cada módulo en su propia tarea (SIGEM-005 a 010) y con nombres en inglés, como `users`. El humano diseñó en Workbench el modelo completo del negocio, con nombres en español, y pidió que la base sea esa.

## Decisión

- Las tablas del negocio se crean todas juntas en SIGEM-018 (migración `0002`), siguiendo el diagrama del humano con los tipos corregidos que exige AGENTS.md §3.
- Tablas y columnas en **español, minúsculas y con `_`** (`detalle_factura`, `id_cliente`). La llave primaria se llama igual que las FK que la apuntan.
- `users` y `refresh_tokens` (SIGEM-004) quedan como están, en inglés: el rol sigue siendo un campo de `users`, sin tabla `Roles`.
- Los atributos de los modelos SQLAlchemy usan el mismo nombre que la columna. La API sigue en inglés (AGENTS.md §4: `/customers`, `/invoices`); los schemas Pydantic traducen.

## Consecuencias

- El diagrama de Workbench (*Reverse Engineer* de `sigem`) coincide con el del humano.
- Conviven nombres en inglés (`users`) y en español en la misma base.
- SIGEM-005 a 010 ya no crean tablas: si necesitan una columna nueva, la agregan con su propia migración.
- Descartado: mayúsculas como en el diagrama (`Detalle_factura`), porque MySQL en Linux distingue mayúsculas en nombres de tabla y en Windows no.
