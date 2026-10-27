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
| 006 | Productos e inventario | CRUD, IVA por producto (0/5/19 %), `CHECK (stock >= 0)`, ajuste manual de stock con motivo | 004 | ✔ inventory |
| 007 | Vendedores | CRUD + desactivar | 004 | |
| 008 | Proveedores | CRUD + desactivar, listado paginado y búsqueda; sin pantalla en Figma: reutiliza el patrón de lista de Vendedores | 004 | |
| 009 | Facturas | Crear factura + descontar stock en una transacción con `FOR UPDATE`, snapshot de items, anular con motivo, test de concurrencia, aviso DIAN | 005–007 | ✔ invoices |
| 010 | Pagos | Pago ≤ saldo con factura bloqueada; estados Pendiente/Parcial/Pagada | 009 | ✔ payments |
| 011 | Dashboard | KPIs y gráficas del prototipo (decidir SVG propio vs. Chart.js) | 009–010 | |
| 012 | Reportes | Excel (openpyxl) y PDF (WeasyPrint/ReportLab) con aviso DIAN | 009–010 | |
| 013 | Auditoría de seguridad de fase | `/claude-security` sobre todo el repo + `agent-skills:security-and-hardening` (OWASP, Ley 1581) | 004–012 | ✔ |
| 014 | QA visual y E2E | Comparar cada pantalla con Figma, Playwright de los flujos principales | 011–012 | |
| 015 | CI | GitHub Actions: ruff, mypy, pytest, ESLint, Vitest, Playwright | 003 (puede adelantarse) | |
| 016 | Despliegue | Docker Compose completo y guía de despliegue gratuito | 014–015 | |
| 017 | Usuarios | Pantalla de usuarios para el Administrador: crear, editar, desactivar, desbloquear y restablecer contraseña (hoy por consola) | 004 | ✔ auth |

## Cómo se replica el diseño de Figma en cada pantalla

1. Leer la pantalla en el prototipo (MCP de Figma, `get_design_context` → `src/App.tsx`, función `<Pantalla>Screen`).
2. Pasarla a HTML semántico con las clases de `css/sigem.css`; los estilos en línea del prototipo se vuelven clases en DESIGN.md (nunca `style=""` con colores sueltos).
3. Aplicar las diferencias deliberadas de DESIGN.md §4.
4. Verificar en el navegador contra la captura del prototipo antes de cerrar la tarea.

## Decisiones de alcance

- **Proveedores (2026-10-25):** entra en v1 como módulo simple (SIGEM-008). El menú lo muestra después de Vendedores, con el icono de camión de la misma familia de iconos.

## Fuera de alcance de v1

Facturación electrónica DIAN, compras a proveedores (órdenes de compra y entradas de inventario), recuperación de contraseña por correo, app móvil, multiempresa.
