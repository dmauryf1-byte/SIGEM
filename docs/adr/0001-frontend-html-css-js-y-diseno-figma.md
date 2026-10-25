# ADR-0001 — Frontend en HTML + CSS + JavaScript y diseño desde Figma

- **Estado:** aceptado por el humano el 2026-10-25
- **Reemplaza en AGENTS.md §1:** React 19 + TypeScript + Vite + Tailwind + shadcn/ui + TanStack + React Hook Form + Zod + React Router

## Contexto

El humano decidió que SIGEM se construye con **HTML, CSS y JavaScript** en la web, **Python** en el backend y **MySQL** como base de datos. También fijó como referencia visual el prototipo de Figma Make *FactuPyme Billing System Prototype* (`figma.com/make/yo56ij2do1azdmmGcViY2i`), que debe replicarse con el nombre **SIGEM**.

## Decisión

| Capa | Antes | Ahora |
|---|---|---|
| Frontend | React 19 + TS + Vite + Tailwind + shadcn/ui | HTML5 + CSS + JavaScript (ES modules nativos), **sin framework ni paso de build** |
| Estilos | Tailwind + shadcn | Un CSS propio con los tokens de `docs/design/DESIGN.md` (sacados del prototipo de Figma) |
| Iconos | lucide-react | Los SVG de línea del prototipo (estilo Feather/Lucide), inline |
| Formularios | React Hook Form + Zod | `<form>` nativo + validación HTML5 en el cliente; **la validación real es la del backend** (Pydantic) |
| Routing | React Router | Una página HTML por pantalla (`clientes.html`, `facturas.html`…) |
| Servidor web | Vite dev server | FastAPI sirve `frontend/` como archivos estáticos (mismo origen: sin CORS) |
| Tooling | ESLint, Prettier, `tsc` | ESLint + Prettier (vía `npm`, solo como herramientas de desarrollo) |
| Tests | Vitest + Testing Library + Playwright | Vitest (lógica JS) + Playwright (E2E) |
| Backend / BD | FastAPI + SQLAlchemy + MySQL 8.4 | **Sin cambios** |

## Consecuencias

- **A favor:** menos dependencias; se ve exactamente lo que se escribe; sin paso de build; el mismo origen simplifica auth con cookies `HttpOnly`.
- **En contra:** sin componentes reutilizables de React. Se compensa con funciones JS pequeñas en `frontend/js/shared/` (render de tablas, modales, toasts) y las clases CSS del prototipo.
- **Seguridad (XSS):** sin React no hay escape automático. Regla nueva en AGENTS.md §5: datos del servidor siempre con `textContent`/`createElement`, nunca con `innerHTML`.
- Se elimina la generación del cliente TypeScript desde OpenAPI; el OpenAPI de FastAPI sigue siendo el contrato.
- La SIGEM-002 (backend + MySQL) no cambia de alcance. SIGEM-003 pasa a ser el frontend en HTML/CSS/JS.

## Pendiente de decidir (en la tarea que lo necesite)

- Gráficas del dashboard y reportes: el prototipo usa Recharts (React). Opciones: SVG/CSS propio o Chart.js. Se decide en la tarea del dashboard.
