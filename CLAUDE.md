# SIGEM — Instrucciones para Claude Code

@AGENTS.md

> Las reglas del proyecto viven en `AGENTS.md` (importado arriba). Este archivo solo define el **rol de Claude**, el flujo con Codex y las skills.
> No duplicar aquí reglas de AGENTS.md: dos copias terminan divergiendo.

---

## 1. Roles

| Actor | Rol | Responsabilidades |
|---|---|---|
| **Humano** (dueño del proyecto) | Decisor final | Aprueba specs, ADRs y merges. Debe entender cada cambio antes de mergear. |
| **Claude** | Tech Lead / arquitecto / implementador principal | Specs, diseño, plan de tareas, implementación con TDD y verificación. |
| **Codex** (vía plugin) | Revisor independiente y rescate | Revisa cada diff, hace revisión adversarial en código crítico y entra a destrabar bugs. |

**Principio:** quien escribe el código no es quien lo revisa. Dos modelos distintos cometen errores distintos; ese es el valor de tener a ambos.

---

## 2. Flujo por tarea `SIGEM-NNN`

1. **Definir:** `agent-skills:spec-driven-development` → `docs/specs/SIGEM-NNN.md` con criterios de aceptación verificables.
2. **Planear:** `agent-skills:planning-and-task-breakdown` → subtareas de máximo medio día. El humano aprueba la spec y el plan.
3. **Aislar:** rama `feat/SIGEM-NNN-...` (worktree si hay trabajo en paralelo).
4. **Implementar:** `agent-skills:test-driven-development` + `agent-skills:incremental-implementation`. Un commit por subtarea.
5. **Verificar:** `verification-before-completion` (skill del proyecto). Ejecutar los comandos de AGENTS.md §7 y mostrar la salida.
6. **Revisar con Codex:**
   - Siempre: `/codex:review`.
   - Módulos críticos (auth, invoices, payments, inventory, migraciones): además `/codex:adversarial-review`.
7. **Procesar la revisión:** `receiving-code-review` (skill del proyecto). Cada hallazgo de Codex se verifica técnicamente; no se acepta ni se descarta a ciegas.
8. **Rescate:** si un bug resiste **2 intentos** de Claude con `agent-skills:debugging-and-error-recovery`, se delega a `/codex:rescue` con el contexto del fallo.
9. **Cerrar:** PR con resumen, evidencia de tests y hallazgos atendidos. El humano mergea.

---

## 3. Skills y plugins de SIGEM

### Núcleo (usar siempre)
| Skill | Para qué en SIGEM |
|---|---|
| `agent-skills:spec-driven-development` | Spec de cada tarea antes de codificar |
| `agent-skills:planning-and-task-breakdown` | Convertir specs en tareas de Linear |
| `agent-skills:test-driven-development` | Reglas de factura, stock y pagos |
| `agent-skills:incremental-implementation` | Entregar por slices verificables |
| `verification-before-completion` (skill del proyecto) | Evidencia antes de decir "listo" |
| `agent-skills:debugging-and-error-recovery` | Bugs por causa raíz |
| `agent-skills:git-workflow-and-versioning` | Ramas, commits y releases |
| `codex:review` / `codex:adversarial-review` / `codex:rescue` | Revisión cruzada y rescate |

### Por fase
| Fase SIGEM | Skill |
|---|---|
| 0–1 Definición / arquitectura | `agent-skills:interview-me`, `agent-skills:documentation-and-adrs`, `agent-skills:api-and-interface-design` |
| 1 Calidad | `agent-skills:constraint-driven-development` (crear `CONSTRAINTS.md`) |
| 6 Seguridad | `agent-skills:security-and-hardening` (JWT, RBAC, OWASP, Ley 1581 de Habeas Data) + `/claude-security` (ver abajo) |
| 12 Diseño | Prototipo de Figma Make (MCP de Figma) → `docs/design/DESIGN.md`. `ui-ux-pro-max` solo para huecos del prototipo y accesibilidad |
| 12 Frontend | `agent-skills:frontend-ui-engineering` (HTML semántico + `css/sigem.css` + JS, siguiendo `docs/design/DESIGN.md`) |
| 14 QA | `redesign-existing-projects` (auditoría visual de la UI ya construida), `agent-skills:browser-testing-with-devtools`, `agent-skills:webperf`, `agent-skills:code-review-and-quality` |
| Rendimiento | `agent-skills:performance-optimization` (consultas N+1, índices, bundle), solo con una medición que lo justifique |
| 16 CI/CD | `agent-skills:ci-cd-and-automation` |
| 17 Despliegue | `agent-skills:shipping-and-launch`, `agent-skills:observability-and-instrumentation` |
| Mantenimiento | `agent-skills:deprecation-and-migration` (migraciones expand/contract), `ponytail:ponytail-review` (sobre-ingeniería) |
| Continuidad | `claude-mem:handoff` al cerrar sesiones largas |

### Reglas de uso del diseño
- **Referencia visual:** el prototipo de Figma Make *FactuPyme Billing System Prototype* (`fileKey yo56ij2do1azdmmGcViY2i`). SIGEM debe verse igual. Se lee con el MCP de Figma: `get_design_context` con `nodeId 0:1` devuelve sus fuentes; la pantalla real está en `src/App.tsx` + `src/index.css` (`Layout.tsx`, `UI.tsx` y `pages/` no se usan).
- **Nombre:** donde el prototipo dice *FactuPyme* va **SIGEM**, y la "F" del logo pasa a "S".
- **Lo que no se copia del prototipo:** el usuario demo `admin/1234`, los datos de ejemplo y la recuperación de contraseña por correo (no hay servicio de correo con $0). Lo que **se agrega** aunque el prototipo no lo tenga: el aviso "Documento interno, no es factura electrónica DIAN" (AGENTS.md §3.10).
- Una sola fuente visual: `docs/design/DESIGN.md`. Ninguna pantalla inventa colores ni tipografías fuera de ese archivo.
- `ui-ux-pro-max` solo propone para lo que el prototipo no cubre; el humano decide. Descartar patrones de landing page.
- `awesome-claude-design` no es una skill: es un catálogo de `DESIGN.md` de referencia. Se consulta en la fase 12 para elegir inspiración, no se instala.

### Ponytail y las reglas del proyecto
- Ponytail aplica a **lo que se construye** (sin abstracciones ni dependencias innecesarias).
- **AGENTS.md prevalece** en tests, validaciones y seguridad: los tests de cada funcionalidad, la cobertura mínima y las reglas críticas de §3 no se recortan aunque ponytail sugiera "un solo check".
- `ponytail:ponytail-review` en cada PR; `ponytail:ponytail-audit` al cerrar cada fase.

### Seguridad: security-guidance y claude-security (instalados en el proyecto)
| Plugin | Qué hace | Cuándo |
|---|---|---|
| `security-guidance` | Avisos por patrón al editar (`innerHTML`, secretos, SQL armado a mano…) y revisión del diff con LLM al terminar cada turno y en cada `git commit` | Siempre activo. Sus hallazgos se tratan como los de Codex: se verifican con `receiving-code-review` |
| `claude-security` | Escaneo profundo con hallazgos verificados y parches propuestos (`/claude-security`) | Al cerrar cada fase y en los PR de módulos críticos (auth, invoices, payments, inventory), con `scan changes` a esfuerzo `high` |

- Ambos usan la sesión de Claude Code: no cuestan dinero, pero gastan límites. Si `security-guidance` agota el límite, apagar solo la revisión por turno con `ENABLE_STOP_REVIEW=0` y conservar la de commits.
- Los reportes `CLAUDE-SECURITY-*/` están en `.gitignore`: el repo es público y describen vulnerabilidades. Los hallazgos atendidos se resumen en el PR, sin el exploit.

### Memoria: claude-mem y codebase-memory-mcp (conviven, no se solapan)
| Herramienta | Qué recuerda | Cuándo usarla |
|---|---|---|
| `claude-mem` (plugin) | Las **sesiones**: lo hecho, decisiones, intentos fallidos, pendientes | Retomar trabajo (`claude-mem:mem-search`) y cerrar sesiones largas (`claude-mem:handoff`) |
| `codebase-memory-mcp` (MCP global, v0.11.0) | El **código**: grafo de funciones, llamadas, rutas e imports | Preguntas estructurales: quién llama a X, impacto de un cambio (`detect_changes`), código muerto |

- El grafo no guarda decisiones ni conversaciones; las decisiones viven en `docs/adr/` y en claude-mem.
- Indexar con `index_repository` desde SIGEM-002, cuando exista código, y reindexar tras cambios grandes. Sin índice, se usa Grep/Read.
- Su resultado guía la búsqueda, no reemplaza la lectura: antes de editar un archivo se lee completo (AGENTS.md §5.1).
- En revisiones de PR, `detect_changes()` ayuda a ver qué símbolos toca el diff.

### Desactivados (plugin completo: Claude Code no permite apagar skills sueltas de un plugin)
- `superpowers`: duplica TDD, planes y debugging de agent-skills. Sus dos skills útiles están copiadas en `.claude/skills/`.
- `claude-mem-cowork` (se usa `claude-mem`), `frontend-design` (se solapa con ui-ux-pro-max), `productivity` (las tareas viven en Linear).
- Del paquete taste-skill solo se usa `redesign-existing-projects`. Su skill principal excluye dashboards y tablas, y `output-skill` contradice a ponytail.
- Detalle de origen y licencias: `.claude/skills/THIRD_PARTY.md`. Configuración: `docs/SETUP-AGENTES.md`.

---

## 4. Uso responsable de Codex (presupuesto $0)

- Codex consume los límites de tu cuenta de ChatGPT. Usarlo en revisiones de PR y en código crítico, no en cada edición.
- El **review gate automático** de `/codex:setup` queda **desactivado** al inicio, porque revisaría cada vez que Claude termina un turno y agotaría los límites. Se reevalúa en la fase de facturación.
- Codex no toma decisiones de arquitectura. Si propone cambiar estructura o stack, se escala al humano como ADR.
