# SIGEM — Reglas del proyecto (fuente única para Claude y Codex)

> **Sistema de Gestión Empresarial y de Facturación** para microempresas en Colombia.
> Proyecto académico con prácticas profesionales. **Presupuesto: $0.** Todo corre en local hasta la fase de despliegue.
> Este archivo lo leen ambos agentes: Codex lo carga de forma nativa y Claude Code lo importa desde `CLAUDE.md`.
> Cualquier cambio aquí es un cambio de reglas: se registra en `docs/adr/`.

---

## 1. Stack (DEFINIDO — no cambiar sin ADR aprobado por el humano)

| Capa | Tecnología |
|---|---|
| Frontend | HTML5 + CSS + JavaScript (ES modules nativos), sin framework ni paso de build ([ADR-0001](docs/adr/0001-frontend-html-css-js-y-diseno-figma.md)) |
| Diseño | Prototipo de Figma Make → tokens y componentes en `docs/design/DESIGN.md` (única fuente visual) |
| Iconos | SVG de línea inline (los del prototipo de Figma) |
| Backend | Python 3.12+, FastAPI, Pydantic v2 (también sirve `frontend/` como estáticos) |
| ORM / migraciones | SQLAlchemy 2.x (estilo 2.0, tipado) + Alembic |
| Base de datos | MySQL Community 8.4 (InnoDB, utf8mb4) |
| Auth | JWT (access corto + refresh) + RBAC; contraseñas con Argon2 o bcrypt |
| Tooling Python | uv (dependencias), ruff (lint + format), mypy (tipos) |
| Tooling JS | ESLint + Prettier (npm solo para herramientas de desarrollo) |
| Tests | Pytest + httpx (back), Vitest (lógica JS), Playwright (E2E) |
| Seguridad | Plugins `security-guidance` (continuo) y `claude-security` (auditorías); ver CLAUDE.md §3 |
| Reportes | openpyxl (Excel), WeasyPrint o ReportLab (PDF) |
| Infra local | Docker + Docker Compose |
| CI | GitHub Actions (nivel gratuito) |
| Gestión | Linear (plan gratuito); IDs `SIGEM-NNN` en ramas y commits |

**Prohibido:** agregar servicios o dependencias de pago, o librerías nuevas sin justificar en el PR.

---

## 2. Arquitectura: monolito modular por capas

La organización es **por módulo de negocio**, no por tipo de archivo. Una carpeta global `services/` con todo mezclado sería un monolito por capas, no uno modular.

```
backend/
  app/
    core/            # config, seguridad (JWT, hashing), DB session, errores, dependencias comunes
    modules/
      customers/
        router.py        # HTTP: entrada/salida, códigos de estado. SIN lógica de negocio.
        schemas.py       # Pydantic: contratos de entrada/salida
        service.py       # Reglas de negocio y transacciones
        repository.py    # Acceso a datos (SQLAlchemy). SIN reglas de negocio.
        models.py        # Modelos ORM
      suppliers/ products/ inventory/ salespeople/ invoices/ payments/ reports/ users/
    main.py
  alembic/
  tests/
    unit/  integration/
frontend/
  index.html               # login
  <modulo>.html            # una página por pantalla: dashboard.html, clientes.html, facturas.html…
  css/sigem.css            # tokens y componentes de docs/design/DESIGN.md
  js/
    shared/                # api.js (fetch + errores), auth.js, layout.js (sidebar/topbar), ui.js (modal, toast, tabla)
    <modulo>.js            # lógica de cada pantalla
  tests/                   # Vitest (unit) y Playwright (e2e)
```

**Reglas de dependencia:**
- `router → service → repository → models`. Nunca saltar capas.
- Un módulo usa otro **solo a través de su `service`** (ej. `invoices.service` llama a `inventory.service`), nunca a su repositorio ni a sus modelos directamente.
- La sesión/transacción la abre y la cierra el **service** (unit of work), no el router ni el repository.

---

## 3. Reglas de negocio críticas (con test obligatorio)

1. **Factura + inventario = una sola transacción.** Crear la factura, insertar sus items y descontar el stock ocurren dentro de la misma transacción; si algo falla, se hace rollback total.
2. **Concurrencia de stock:** las filas de producto se leen con `SELECT ... FOR UPDATE` (`with_for_update()`) antes de descontar. Requiere un test de concurrencia (dos ventas simultáneas del último ítem).
3. **Stock nunca negativo:** validar en el service y además con una restricción `CHECK (stock >= 0)` en la BD.
4. **Pago ≤ saldo pendiente.** El saldo se calcula como `total - SUM(pagos)` dentro de la transacción, con la factura bloqueada.
5. **Dinero = `DECIMAL(14,2)` en MySQL y `Decimal` en Python.** Prohibido `float` para montos. El redondeo se define en un solo lugar (`core/money.py`).
6. **Snapshot en `invoice_items`:** guardar `unit_price`, `tax_rate` y la descripción vigentes al facturar. Cambiar el precio de un producto no altera facturas históricas.
7. **IVA por producto** (tarifas 0 %, 5 % y 19 %), no uno global.
8. **Las facturas no se borran.** Se anulan con estado y motivo.
9. **Clientes, productos, proveedores y vendedores con historial se desactivan (`is_active`), no se eliminan.**
10. **Alcance legal:** SIGEM v1 genera documentos de venta internos. **No es facturación electrónica DIAN**, y debe indicarse así en la UI y en los PDF hasta que exista una integración.

---

## 4. Contrato de API

- Prefijo `/api/v1`. Recursos en plural e inglés (`/customers`, `/invoices/{id}/payments`).
- Creación correcta → `201` + objeto completo. Validación → `422`. Regla de negocio violada → `409` o `422` con código. Sin permiso → `403`. No autenticado → `401`.
- Formato de error único:
  ```json
  { "errors": [ { "field": "email", "code": "invalid_format", "message": "El correo no es válido" } ] }
  ```
- Toda FK recibida (`customer_id`, `product_id`…) se valida contra la BD y responde un error claro si no existe.
- Listados paginados (`?page=&size=`) desde el primer endpoint.
- Los permisos se validan **siempre en el backend**. El frontend solo oculta opciones.
- El OpenAPI generado por FastAPI es el contrato oficial; `frontend/js/shared/api.js` lo consume.

---

## 5. Reglas para cualquier agente (Claude o Codex)

1. Leer el código existente y este archivo antes de modificar nada.
2. No cambiar arquitectura, stack ni estructura sin autorización explícita del humano.
3. Todo cambio de esquema pasa por una migración Alembic revisada a mano (el autogenerate se revisa, nunca se confía a ciegas).
4. Toda funcionalidad lleva tests. Cada bug se corrige primero con un test que lo reproduce.
5. Cambios pequeños: un PR = una tarea `SIGEM-NNN`.
6. Python con type hints completos. Prohibido `# type: ignore`, `eslint-disable` o tests en `skip` sin justificación escrita en el PR.
7. **XSS:** en el frontend, los datos que vienen del servidor o del usuario se pintan con `textContent` o `createElement`, **nunca** con `innerHTML`, `outerHTML`, `insertAdjacentHTML` ni `document.write`. El token de sesión va en cookie `HttpOnly`, nunca en `localStorage`.
8. Nunca secretos en Git. `.env` va en `.gitignore`; `.env.example` se mantiene actualizado.
9. No eliminar funcionalidad existente sin autorización.
10. No declarar una tarea terminada sin mostrar la salida real de los comandos de verificación (sección 7).
11. Si falta contexto o hay ambigüedad: **detenerse y preguntar**, no inventar requerimientos.

---

## 6. Git

- `main` siempre estable y protegida. Ramas `feat/SIGEM-NNN-descripcion`, `fix/SIGEM-NNN-...`.
- Conventional Commits: `feat(invoices): crear factura con descuento de stock (SIGEM-031)`.
- Merge solo con CI en verde y aprobación del humano. Squash merge.
- Versionado SemVer con tags `vX.Y.Z` desde la primera versión funcional.

---

## 7. Comandos de verificación (Definition of Done técnico)

```bash
# Backend
cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app && uv run pytest --cov=app

# Frontend (sin build: el navegador carga los archivos tal cual)
cd frontend && npm run lint && npm run format:check && npm run test -- --run

# E2E (con docker compose up)
cd frontend && npx playwright test
```

**Definition of Done:** criterios de aceptación cumplidos · tests nuevos en verde · comandos anteriores en verde · migración incluida si aplica · documentación actualizada si aplica · revisión cruzada hecha · el humano entiende el cambio.

**Cobertura mínima:** 80 % en `service.py` de cada módulo; 100 % de las reglas de la sección 3.

---

## 8. Estado actual

- **Fase:** 0–2 (definición y herramientas).
- **Completada:** SIGEM-001, entorno local de Windows verificado (`scripts/verificar-entorno.ps1` en `LISTO`) y repo en GitHub con `main` protegida (solo PR + squash merge).
- **Cambio de stack (2026-10-25):** frontend en HTML + CSS + JavaScript y diseño del prototipo de Figma ([ADR-0001](docs/adr/0001-frontend-html-css-js-y-diseno-figma.md)). Plan completo en `docs/PLAN.md`.
- **Tarea en curso:** SIGEM-002, estructura del backend (`backend/`, `docker-compose.yml` con MySQL 8.4) y prueba real FastAPI → MySQL. Después, SIGEM-003: esqueleto del frontend con el layout de Figma.
- **No** escribir módulos de negocio hasta completar SIGEM-002 (repositorio y estructura) y la prueba real FastAPI → MySQL.
