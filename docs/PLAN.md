# SIGEM — Plan de trabajo

> Stack: HTML + CSS + JavaScript (web) · Python/FastAPI (backend) · MySQL 8.4 · diseño del prototipo de Figma ([ADR-0001](adr/0001-frontend-html-css-js-y-diseno-figma.md)).
> Cada tarea sigue el flujo de CLAUDE.md §2: spec → plan → rama → TDD → verificación → Codex (+ `security-guidance` siempre, `/claude-security` en críticos) → PR → el humano mergea.
> Los números de tarea son una propuesta: se crean en Linear cuando el humano aprueba cada spec.

## Orden de las tareas

| # | Tarea | Qué entrega | Depende de | Crítica |
|---|---|---|---|---|
| 002 | Estructura del backend | FastAPI + MySQL en Docker; `GET /api/v1/health` 200/503 con tests | — | |
| 003 | Esqueleto del frontend | `frontend/` servido por FastAPI; `css/sigem.css` con los tokens de DESIGN.md; layout (sidebar + barra superior) y login **solo visuales**, iguales a Figma; ESLint, Prettier, Vitest y Playwright | 002 | |
| 004 | Usuarios y autenticación | Tabla `users`, Argon2, JWT en cookie `HttpOnly` + refresh, RBAC (Administrador / Vendedor), login real | 003 | ✔ auth |
| 005 | Clientes | CRUD + desactivar, listado paginado y búsqueda; pantalla igual a Figma | 004 | |
| 006 | Productos e inventario | CRUD, IVA por producto (0/5/19 %), `CHECK (stock >= 0)` | 004 | ✔ inventory |
| 007 | Vendedores | CRUD + desactivar | 004 | |
| 008 | Facturas | Crear factura + descontar stock en una transacción con `FOR UPDATE`, snapshot de items, anular con motivo, test de concurrencia, aviso DIAN | 005–007 | ✔ invoices |
| 009 | Pagos | Pago ≤ saldo con factura bloqueada; estados Pendiente/Parcial/Pagada | 008 | ✔ payments |
| 010 | Dashboard | KPIs y gráficas del prototipo (decidir SVG propio vs. Chart.js) | 008–009 | |
| 011 | Reportes | Excel (openpyxl) y PDF (WeasyPrint/ReportLab) con aviso DIAN | 008–009 | |
| 012 | Auditoría de seguridad de fase | `/claude-security` sobre todo el repo + `agent-skills:security-and-hardening` (OWASP, Ley 1581) | 004–011 | ✔ |
| 013 | QA visual y E2E | Comparar cada pantalla con Figma, Playwright de los flujos principales | 010–011 | |
| 014 | CI | GitHub Actions: ruff, mypy, pytest, ESLint, Vitest, Playwright | 003 (puede adelantarse) | |
| 015 | Despliegue | Docker Compose completo y guía de despliegue gratuito | 013–014 | |

## Cómo se replica el diseño de Figma en cada pantalla

1. Leer la pantalla en el prototipo (MCP de Figma, `get_design_context` → `src/App.tsx`, función `<Pantalla>Screen`).
2. Pasarla a HTML semántico con las clases de `css/sigem.css`; los estilos en línea del prototipo se vuelven clases en DESIGN.md (nunca `style=""` con colores sueltos).
3. Aplicar las diferencias deliberadas de DESIGN.md §4.
4. Verificar en el navegador contra la captura del prototipo antes de cerrar la tarea.

## Por decidir

- **Proveedores:** AGENTS.md §2 lo incluye como módulo, pero el prototipo de Figma no tiene esa pantalla. El humano decide si entra en v1 (con el patrón de las pantallas de lista) o se aplaza.

## Fuera de alcance de v1

Facturación electrónica DIAN, recuperación de contraseña por correo, app móvil, multiempresa.
