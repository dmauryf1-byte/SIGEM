# SIGEM — Sistema de diseño

> **Única fuente visual** (CLAUDE.md §3). Valores copiados del prototipo de Figma Make *FactuPyme Billing System Prototype* (`fileKey yo56ij2do1azdmmGcViY2i`, archivos `src/App.tsx` + `src/index.css`). SIGEM debe verse igual; solo cambia el nombre.
> Si un valor no está aquí, se agrega aquí primero (con su origen) y después se usa.

## 1. Tokens (`frontend/css/sigem.css`, en `:root`)

### Color
| Token | Valor | Uso |
|---|---|---|
| `--primary` | `#3B82F6` | Botón principal, ítem activo del menú, logo, enlaces, foco |
| `--primary-dark` | `#2563EB` | Hover del botón principal; texto del avatar de la barra superior |
| `--sidebar` | `#1E293B` | Fondo del menú lateral |
| `--sidebar-hover` | `#334155` | Hover del menú y borde superior del bloque de usuario |
| `--page-bg` | `#F1F5F9` | Fondo del área de contenido |
| `--surface` | `#FFFFFF` | Tarjetas, barra superior, modales, inputs |
| `--surface-alt` | `#F8FAFC` | Cabecera de tablas, hover de filas, cajas informativas |
| `--border` | `#E2E8F0` | Bordes de tarjetas, tablas y barra superior |
| `--border-input` | `#D1D5DB` | Bordes de inputs y botón secundario |
| `--text` | `#0F172A` | Títulos y texto principal |
| `--text-body` | `#374151` | Celdas de tabla, etiquetas de formulario |
| `--text-muted` | `#64748B` | Subtítulos, cabeceras de tabla, textos de apoyo |
| `--text-subtle` | `#94A3B8` | Ítems inactivos del menú, placeholders, iconos de búsqueda |
| `--success` | `#10B981` | Variaciones positivas en KPIs |
| `--warning` | `#F59E0B` | Stock bajo |
| `--danger` | `#EF4444` | Errores, "Cerrar sesión", campo obligatorio `*`, stock en 0 |
| `--violet` | `#8B5CF6` | Icono del KPI "Pagos recibidos" |

### Badges y alertas (fondo / texto)
| Variante | Fondo | Texto | Borde (alertas) |
|---|---|---|---|
| green / success | `#D1FAE5` | `#065F46` | `#A7F3D0` |
| red / error | `#FEE2E2` | `#991B1B` | `#FECACA` |
| yellow / warning | `#FEF3C7` | `#92400E` | `#FDE68A` |
| blue / info | `#DBEAFE` | `#1E40AF` | `#BFDBFE` |
| gray | `#F1F5F9` | `#475569` | — |
| purple | `#EDE9FE` | `#5B21B6` | — |

Estado → badge: Pagada = green · Pendiente = yellow · Parcial = blue · Anulada = red · Activo = green · Inactivo = gray.

### Tipografía
- **Texto:** `Inter` (300–700). **Títulos y cifras:** `DM Sans` (400–700). Ambas de Google Fonts.
- Título de página (barra superior): DM Sans 700, 17 px; subtítulo 12 px `--text-muted`.
- Título dentro de la página: DM Sans 700, 22 px. Título de tarjeta: DM Sans 700, 15 px. Título de modal: DM Sans 700, 18 px.
- Valor de KPI: DM Sans 700, 24 px. Etiqueta de KPI: 12 px, 500, mayúsculas, `letter-spacing: .05em`.
- Cuerpo y celdas: 14 px. Cabecera de tabla: 12 px, 600, mayúsculas, `letter-spacing: .05em`. Etiqueta de formulario: 13 px, 500.

### Forma
- Radios: botones e inputs 8 px · tarjetas 12 px · modal 14 px · logo 10 px · badges 999 px · `btn-icon` 6 px.
- Sombras: tarjeta `0 1px 3px rgba(0,0,0,.06)` · modal `0 20px 60px rgba(0,0,0,.2)` · foco de input `0 0 0 3px rgba(59,130,246,.12)`.
- Transiciones: `0.15s ease`.

## 2. Layout

```
┌──────────┬──────────────────────────────────────────────┐
│ Sidebar  │ Barra superior (60 px, blanca, sticky)        │
│ 232 px   │  Título + subtítulo      [acciones] 🔔 (A)    │
│ #1E293B  ├──────────────────────────────────────────────┤
│ Logo S   │ Contenido: padding 28 px, fondo --page-bg     │
│ Menú     │                                               │
│ ──────── │                                               │
│ Usuario  │                                               │
│ Salir    │                                               │
└──────────┴──────────────────────────────────────────────┘
```

- **Sidebar:** logo = cuadro 36×36 `--primary`, radio 10, letra **"S"** blanca DM Sans 800 16 px; al lado "SIGEM" (DM Sans 700 16 px `#F1F5F9`) y debajo "Sistema de gestión empresarial" (11 px `--text-muted`).
- **Menú** (en este orden, icono 18 px + texto): Inicio · Clientes · Productos · Vendedores · Proveedores · Facturas · Pagos · Reportes · Usuarios (este último solo para Administrador; el backend también lo bloquea). Ítem: padding 10×16, radio 8, 14 px 500, `--text-subtle`; hover `--sidebar-hover` con texto `#F1F5F9`; activo `--primary` con texto blanco. Ítem sin pantalla todavía (SIGEM-003): `aria-disabled="true"`, opacidad 0.45, sin hover (no está en el prototipo).
- **Foco de teclado** (no está en el prototipo, WCAG 2.4.7): `outline: 2px solid --primary`, `outline-offset: 2px` en `:focus-visible`.
- **Pie del sidebar:** avatar redondo 34 px `--primary` con la inicial; nombre (13 px 600) y rol (11 px); "Cerrar sesión" en `--danger`.
- **Barra superior:** a la derecha, acciones de la pantalla (ej. "+ Nueva factura"), campana en `btn-icon` con punto rojo, avatar 34 px fondo `#DBEAFE` letra `--primary-dark`.
- **Login:** fondo `linear-gradient(135deg, #1E293B, #0F172A)` con dos halos radiales (azul y verde); logo 56×56 radio 16 con sombra azul; "SIGEM" DM Sans 800 26 px; tarjeta blanca radio 16, padding 32, ancho máx. 420.

## 3. Componentes (clases CSS del prototipo, se conservan los nombres)

`card`, `stat-card`, `kpi-icon-wrap` (44×44, radio 10), `btn-primary`, `btn-secondary`, `btn-danger`, `btn-icon` (32×32), `form-input` (+ `.error`), `form-label`, `form-error`, `select-input`, `search-input-wrap`, `table-base`, `badge` + `badge-{green,red,yellow,blue,gray,purple}`, `alert` + `alert-{success,error,warning,info}`, `modal-overlay`, `modal-box`, `tabs`, `tab-btn`, `page-header`, `page-title`, `page-subtitle`, `sidebar-item`.

Los valores exactos de cada clase están en `src/index.css` del prototipo y se copian tal cual a `frontend/css/sigem.css`.

- **Dashboard:** fila de 4 KPIs (grid 4 columnas, gap 16) → fila con "Ventas del mes" (área) y "Ventas por categoría" (dona 320 px) → fila con "Facturas recientes" y "Productos con stock bajo". Colores de la dona: `#3B82F6`, `#10B981`, `#F59E0B`.
- **Pantallas de lista:** barra superior con botón "+ Nuevo…", tarjeta con buscador y filtros, `table-base`, acciones por fila con `btn-icon` (ver, editar, desactivar), formularios en `modal-box`.
- **Confirmación:** modal de 400 px con círculo de icono 44 px (rojo si es destructivo, ámbar si no).
- **Dinero:** `$` + separador de miles `es-CO`, sin decimales en pantalla (ej. `$2.345.000`). El cálculo nunca se hace en el cliente (AGENTS.md §3.5).

## 4. Diferencias deliberadas con el prototipo

| Prototipo | SIGEM | Motivo |
|---|---|---|
| "FactuPyme", logo "F" | "SIGEM", logo "S" | Nombre del proyecto |
| Usuario demo `admin/1234` en el login | Se elimina | Seguridad |
| "¿Olvidaste tu contraseña?" por correo | Se oculta en v1; el administrador restablece | Sin servicio de correo ($0) |
| Sin aviso legal | "Documento interno — no es factura electrónica DIAN" en facturas y PDF; en el login, bajo la tarjeta, "SIGEM genera documentos de venta internos. No es facturación electrónica DIAN." (12 px, `--text-subtle`) | AGENTS.md §3.10 |
| Estado de factura "Vencida" | Pendiente / Parcial / Pagada / Anulada | Reglas de pago de AGENTS.md §3 |
| Sin módulo de proveedores | Ítem "Proveedores" (icono `truck` de Feather) con la pantalla de lista estándar | Requisito de SIGEM (PLAN.md, SIGEM-008) |
| Ancho fijo de escritorio | Mismo diseño; mínimo soportado 1280 px | App interna de escritorio |
