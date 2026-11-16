# SIGEM-018 — Modelo de datos completo (diagrama del humano)

- **Estado:** aprobada por el humano (2026-11-16)
- **Rama:** `feat/SIGEM-018-modelo-de-datos` (sobre `feat/SIGEM-004-auth-jwt-rbac`: necesita la migración `0001`; se rebasa sobre `main` cuando se mergee SIGEM-004)
- **Depende de:** SIGEM-004 · **Adelanta las tablas de:** SIGEM-005 a SIGEM-010
- **Módulos críticos (invoices, payments, inventory):** `/codex:review` + `/codex:adversarial-review` + `/claude-security` (scan changes, esfuerzo high)

## Objetivo

Crear en la MySQL de SIGEM todas las tablas del negocio según el diagrama del humano (`docs/specs/img/SIGEM-018-diagrama.png`), ajustado a las reglas de AGENTS.md §3. Las tareas 005–010 ya no crean tablas: construyen servicio, API y pantalla sobre estas.

El éxito se demuestra así: `alembic upgrade head` crea las 7 tablas; en Workbench, *Database → Reverse Engineer* sobre `sigem` muestra el mismo diagrama; `alembic downgrade 0001` las borra sin tocar `users` ni `refresh_tokens`.

### Fuera de alcance
- Servicios, endpoints y pantallas (siguen en SIGEM-005 a SIGEM-010).
- Tabla `Roles` y cambios a `users`: se mantiene la de SIGEM-004, con el rol como enum (decisión del humano 2026-11-16).

## Decisiones (del humano, 2026-11-16)

| Decisión | Elegido | Descartado |
|---|---|---|
| Fidelidad | Mismas tablas, columnas y relaciones del diagrama, con los tipos corregidos que exige AGENTS.md §3 | Copia exacta con `FLOAT`: errores de redondeo en dinero |
| Idioma | Nombres en español, como el diagrama | Inglés: no es como lo pidió el humano. `users` y `refresh_tokens` quedan en inglés (ya existen) |
| Formato de nombres | Minúsculas con `_` (`detalle_factura`, `id_cliente`) | Mayúsculas como `Detalle_factura`: MySQL en Linux distingue mayúsculas en nombres de tabla y en Windows no; mezclarlas da errores al pasar de un equipo a otro |
| Llave primaria | `id_<tabla en singular>` igual al nombre de la FK que la apunta (`clientes.id_cliente` ↔ `factura.id_cliente`) | `id_Clientes` vs `id_cliente` del diagrama: dos nombres para lo mismo |
| Cómo se crea | Migración Alembic `0002` revisada a mano + modelos SQLAlchemy en el `models.py` de cada módulo | Crear en Workbench y exportar: AGENTS.md §5.3; sin modelos, el próximo `--autogenerate` propondría borrar las tablas |
| Borrado | Todas las FK con `ON DELETE RESTRICT`: nada con historial se borra (§3.8, §3.9) | `CASCADE` |

## Cambios respecto al diagrama

| Tabla.columna | Diagrama | Queda | Por qué |
|---|---|---|---|
| Todos los montos (`subtotal`, `impuesto`, `descuento`, `total`, `total_pagado`, `saldo`, `precio_*`, `valor`) | `FLOAT` | `DECIMAL(14,2)` | §3.5 |
| `porcentaje_comision`, `porcentaje_impuesto` | `DECIMAL` / `FLOAT` | `DECIMAL(5,2)`, entre 0 y 100 | Porcentaje exacto |
| `telefono` (clientes, vendedor, proveedor) | `INT` | `VARCHAR(20)` | 3001234567 no cabe en `INT`; también lleva `+57` o ceros |
| `documento_id` (clientes, proveedor) | `INT` | `VARCHAR(20)` | NIT con dígito de verificación (`900123456-7`) y ceros a la izquierda |
| `DATETIME(10)` / `DATETIME(20)` | — | `DATETIME` | MySQL solo admite precisión 0–6; esos valores fallan |
| `pagos.fecha_creacion` | `VARCHAR(45)` | `DATETIME` | Es una fecha |
| `detalle_factura.cantidad` | `FLOAT` | `INT`, `> 0` | El stock es `INT` |
| `producto.porcentaje_iva` | no existe | **Nueva**, `DECIMAL(5,2)` ∈ {0, 5, 19} | §3.7 IVA por producto |
| `producto.stock` | `INT` | `INT` + `CHECK (stock >= 0)` | §3.3 |
| `detalle_factura.descripcion` | no existe | **Nueva**, `VARCHAR(45)` | §3.6 snapshot (precio e IVA ya están en el detalle) |
| `factura.motivo_anulacion`, `factura.fecha_anulacion` | no existen | **Nuevas**, opcionales | §3.8 anular con motivo |
| `factura.estado` | `VARCHAR(45)` libre | `VARCHAR(45)` ∈ {Pendiente, Parcial, Pagada, Anulada} | PLAN.md SIGEM-010 |
| `factura.numero_factura` | — | Único | No puede haber dos facturas con el mismo número |
| `clientes`, `proveedor` | — | Único (`tipo_documento`, `documento_id`) | No registrar dos veces al mismo |
| `pagos.valor` | — | `> 0` | Un pago de 0 o negativo no tiene sentido |

`factura.total_pagado` y `factura.saldo` se mantienen como en el diagrama. El service los actualiza en la misma transacción que el pago, con la factura bloqueada (§3.4).

## Tablas resultantes

Opcional = puede quedar vacío (rombo blanco en el diagrama). El resto es obligatorio. Todas las tablas con `activo` usan `TINYINT(1)` con valor por defecto 1. `fecha_creacion` y la de actualización las pone MySQL.

- **clientes:** `id_cliente`, `nombre` (255), `tipo_documento` (45), `documento_id` (20), `razon_social` (150, opcional), `direccion` (100), `telefono` (20), `ciudad` (45, opcional), `activo`, `fecha_creacion`, `ultima_actualizacion`
- **vendedor:** `id_vendedor`, `tipo_documento` (45), `documento_id` (45), `nombre` (75), `email` (150), `telefono` (20), `porcentaje_comision`, `activo`, `fecha_creacion`, `fecha_actualizacion`
- **proveedor:** `id_proveedor`, `tipo_documento` (45), `documento_id` (20), `razon_social` (45), `nombre_contacto` (45), `email` (150), `telefono` (20), `direccion` (150), `ciudad` (150), `activo`, `fecha_creacion`, `ultima_actualizacion`
- **producto:** `id_producto`, `id_proveedor` → proveedor, `nombre` (45), `precio_compra`, `precio_venta`, `porcentaje_iva`, `stock`, `activo`, `fecha_creacion`, `fecha_actualizacion`
- **factura:** `id_factura`, `id_cliente` → clientes, `id_vendedor` → vendedor, `numero_factura` (255), `fecha_factura`, `subtotal`, `impuesto`, `descuento`, `total`, `total_pagado`, `saldo`, `estado`, `notas` (45, opcional), `motivo_anulacion` (255, opcional), `fecha_anulacion` (opcional), `fecha_creacion`, `ultima_actualizacion`
- **detalle_factura:** `id_detalle_factura`, `id_factura` → factura, `id_producto` → producto, `descripcion` (45), `cantidad`, `precio_unitario`, `descuento`, `porcentaje_impuesto`, `impuesto`, `subtotal`, `total`
- **pagos:** `id_pago`, `id_factura` → factura, `fecha_pago`, `valor`, `metodo_pago` (45), `referencia` (45, opcional), `notas` (45, opcional), `fecha_creacion`

## Criterios de aceptación

1. `alembic upgrade head` sobre una base con `0001` crea las 7 tablas con las columnas, tipos, FK, únicos y `CHECK` de arriba.
2. `alembic downgrade 0001` las borra y deja `users` y `refresh_tokens` intactas; `upgrade` de nuevo funciona.
3. Tests de integración contra MySQL real demuestran que la BD rechaza: stock negativo, IVA distinto de 0/5/19, cantidad ≤ 0, pago ≤ 0, estado inválido, FK inexistente, documento o número de factura repetido, y borrar un cliente con facturas.
4. Un test compara los modelos SQLAlchemy con la base migrada (Alembic `compare_metadata`) y no encuentra diferencias.
5. Comandos de AGENTS.md §7 en verde.
6. En Workbench, *Reverse Engineer* de `sigem` muestra las 7 tablas y sus relaciones como el diagrama.

## Archivos

```
backend/app/modules/{customers,salespeople,suppliers,products,invoices,payments}/models.py
backend/alembic/env.py                          # importa los modelos nuevos
backend/alembic/versions/0002_modelo_de_datos.py
backend/tests/integration/test_modelo_de_datos.py
docs/adr/0003-nombres-de-bd-en-espanol.md
docs/PLAN.md                                    # SIGEM-018 y 005–010 sin creación de tablas
```
