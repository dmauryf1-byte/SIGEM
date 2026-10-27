# SIGEM-003 — Esqueleto del frontend con el diseño de Figma

- **Estado:** aprobada (2026-10-27, el humano delegó la aprobación tras la revisión de Claude)
- **Rama:** `feat/SIGEM-003-esqueleto-frontend` (sobre `main`, con SIGEM-002 ya mergeada)
- **Depende de:** SIGEM-002 · **Bloquea a:** SIGEM-004 en adelante

## Objetivo

Dejar el frontend listo para que cada módulo solo agregue su página: FastAPI sirve `frontend/`, y el **login** y el **marco de la aplicación** (sidebar + barra superior) se ven igual que el prototipo de Figma, con el nombre SIGEM.

El éxito se demuestra abriendo `http://localhost:8000/` con el servidor del backend: aparece el login de SIGEM, y `dashboard.html` muestra el marco con "Inicio" activo. Playwright comprueba los valores de DESIGN.md (colores, medidas) en el navegador.

### Fuera de alcance
- Login real, sesión y permisos: SIGEM-004. Aquí el formulario solo valida campos vacíos.
- Contenido del dashboard (KPIs, gráficas): SIGEM-011. Aquí el área de contenido queda con un estado vacío.
- Pantallas de módulos: cada una llega con su tarea.

## Decisiones

| Decisión | Elegido | Descartado y por qué |
|---|---|---|
| Quién sirve el frontend | FastAPI con `StaticFiles(html=True)` montado en `/`, después de `/api/v1` | Servidor aparte (Vite, nginx): dos procesos y CORS sin necesidad |
| Sidebar y barra superior | Las genera `js/shared/layout.js` con `createElement` en cada página | Copiar el HTML en cada página: 10 copias que divergen |
| Ítems del menú sin pantalla todavía | Visibles pero deshabilitados (`aria-disabled="true"`); cada tarea de módulo habilita el suyo | Enlaces a páginas que dan 404 |
| Fuentes | Google Fonts (Inter + DM Sans), igual que el prototipo | Autoalojarlas: más archivos sin necesidad medida |
| Iconos | Los SVG del prototipo, en `js/shared/icons.js` | Librería de iconos: dependencia para 20 iconos |

## Stack de esta tarea

| Pieza | Detalle |
|---|---|
| Navegador | HTML5, CSS, JavaScript ES modules (`<script type="module">`), sin build |
| Dev (npm) | `eslint`, `prettier`, `vitest` + `jsdom`, `@playwright/test` (solo Chromium) |
| Backend | Solo se agrega el montaje de estáticos en `app/main.py` |

## Estructura

```
frontend/
  package.json            # scripts: lint, format:check, test, e2e
  eslint.config.js
  playwright.config.js    # arranca el backend con uvicorn antes de los tests
  index.html              # login
  dashboard.html          # marco de la app + estado vacío
  css/sigem.css           # tokens (:root) y clases de DESIGN.md
  js/
    shared/icons.js       # SVG del prototipo
    shared/layout.js      # renderSidebar(), renderTopBar()
    login.js              # validación de campos vacíos
    dashboard.js
  tests/
    unit/layout.test.js   # Vitest + jsdom
    e2e/shell.spec.js     # Playwright
backend/app/main.py       # + app.mount("/", StaticFiles(directory=…/frontend, html=True))
```

## Estilo de código

```js
// js/shared/layout.js — sin innerHTML con datos (AGENTS.md §5.7)
export const NAV_ITEMS = [
  { key: 'dashboard', label: 'Inicio', icon: 'home', href: 'dashboard.html' },
  { key: 'clientes', label: 'Clientes', icon: 'users', href: null }, // null = aún sin pantalla
  // …
];

export function renderSidebar(container, { current, user }) {
  const nav = document.createElement('nav');
  nav.setAttribute('aria-label', 'Módulos');
  // …un <a class="sidebar-item"> por ítem; activo con aria-current="page"
  container.replaceChildren(nav);
}
```

- Clases y valores exactamente los de DESIGN.md; nada de `style=""` con colores.
- Textos al usuario en español; nombres de código en inglés salvo las claves del menú.
- Accesible: `<label for>` en cada input, foco visible, `aria-current` en el ítem activo, contraste AA.

## Estrategia de tests

| Nivel | Qué cubre | Dónde |
|---|---|---|
| Unit (Vitest) | El sidebar marca activo solo el ítem actual; los ítems sin pantalla salen deshabilitados; "Usuarios" solo aparece para Administrador; el nombre del usuario se pinta como texto (un nombre con `<img onerror>` no crea elementos) | `tests/unit/layout.test.js` |
| E2E (Playwright) | `/` muestra el login de SIGEM sin el usuario demo; enviar vacío muestra los dos errores; `dashboard.html` muestra el marco; estilos calculados = DESIGN.md (sidebar `rgb(30, 41, 59)` y 232 px, barra superior 60 px, ítem activo `rgb(59, 130, 246)`, fuente DM Sans en títulos) | `tests/e2e/shell.spec.js` |
| Backend (pytest) | `/api/v1/health` sigue respondiendo con los estáticos montados; `/` devuelve el HTML del login | `tests/integration/test_frontend.py` |

## Comandos

```powershell
docker compose up -d mysql
cd backend;  uv run fastapi dev app/main.py          # http://localhost:8000/
cd frontend; npm install; npx playwright install chromium
npm run lint; npm run format:check; npm run test -- --run; npx playwright test
```

## Límites

- **Siempre:** comparar cada pantalla con el código del prototipo (`App.tsx`: `LoginScreen`, `Sidebar`, `TopBar`, `AppShell`) y con DESIGN.md.
- **Preguntar antes:** cualquier dependencia npm fuera de la lista; cualquier diferencia visual con Figma no listada en DESIGN.md §4.
- **Nunca:** `innerHTML` con datos; guardar tokens en `localStorage`; copiar el usuario demo `admin/1234`.

## Criterios de aceptación

1. Con el backend arriba, `http://localhost:8000/` muestra el login de SIGEM igual al prototipo: fondo degradado, logo "S", "SIGEM", tarjeta blanca de 420 px, sin el recuadro "Demo: admin / 1234" ni "¿Olvidaste tu contraseña?".
2. Enviar el login vacío muestra "El usuario es obligatorio" y "La contraseña es obligatoria" bajo cada campo.
3. `dashboard.html` muestra el sidebar (logo, 9 ítems en el orden de DESIGN.md, usuario y "Cerrar sesión") y la barra superior con título "Dashboard"; "Inicio" activo.
4. `/api/v1/health` sigue en `200` con los estáticos montados.
5. `npm run lint`, `npm run format:check`, `npm run test -- --run` y `npx playwright test` en verde; también los comandos del backend de AGENTS.md §7. Salida pegada en el PR.
6. Revisión visual: capturas de login y dashboard en el PR.
7. AGENTS.md §8 actualizado: SIGEM-003 completada; siguiente, SIGEM-004.

## Preguntas abiertas

- Ninguna. El usuario que muestra el sidebar es fijo ("Administrador") hasta SIGEM-004, que lo toma de la sesión.
- Hasta SIGEM-004: el login con ambos campos llenos no navega (no hay sesión que crear) y "Cerrar sesión" enlaza a `index.html`.

## Plan de subtareas (un commit cada una)

1. **Backend sirve `frontend/`:** test pytest (`/` da HTML, health sigue 200) → montaje en `main.py` + `index.html` mínimo.
2. **Tooling npm:** `package.json`, ESLint, Prettier, Vitest, Playwright; `npm run lint/format:check/test` corren.
3. **CSS e iconos:** `css/sigem.css` con tokens y clases del prototipo; `js/shared/icons.js`.
4. **Login:** `index.html` + `login.js` según `LoginScreen`, con validación de vacíos.
5. **Marco:** `layout.js` con tests unitarios (TDD) + `dashboard.html`.
6. **E2E y cierre:** `shell.spec.js`, capturas, AGENTS.md §8.
