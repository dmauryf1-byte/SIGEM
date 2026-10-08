# SIGEM — Configuración de agentes (Claude Code + Codex)

Ejecutar en PowerShell, desde la raíz del repo `sigem/`. Todo es gratuito salvo los límites de tus cuentas de Claude y ChatGPT.

## 1. Copiar la configuración al repo

Descomprime `sigem-agentes.zip` en la raíz de `sigem/`. Debe quedar:

```
sigem/
├── AGENTS.md
├── CLAUDE.md
├── .claude/skills/   (ui-ux-pro-max, redesign-existing-projects, verification-before-completion, receiving-code-review)
├── docs/SETUP-AGENTES.md
└── scripts/verificar-entorno.ps1
```

Las skills en `.claude/skills/` se cargan solas en cualquier sesión abierta dentro del repo. No requieren instalación.

## 2. Plugins: qué queda activo

```powershell
claude plugin list          # mira los IDs exactos (name@marketplace o name@synced)
```

| Plugin | Estado | Motivo |
|---|---|---|
| agent-skills | **activo** | Base de ingeniería: specs, planes, TDD, debugging, seguridad, CI/CD |
| codex (openai) | **activo** | Revisión cruzada y rescate |
| ponytail | **activo** | Revisión de sobre-ingeniería bajo demanda |
| claude-mem | activo (opcional) | Memoria entre sesiones |
| superpowers | **desactivado** | Duplica TDD, planes y debugging de agent-skills; sus 2 skills útiles están vendorizadas |
| claude-mem-cowork | **desactivado** | Duplica claude-mem |
| frontend-design | **desactivado** | Se solapa con ui-ux-pro-max: una sola voz de diseño |
| productivity | **desactivado** | Las tareas viven en Linear |

Desactivar en este proyecto (usa el ID exacto que mostró `claude plugin list`; los sincronizados desde claude.ai terminan en `@synced`):

```powershell
claude plugin disable superpowers --scope project
claude plugin disable claude-mem-cowork --scope project
claude plugin disable frontend-design --scope project
claude plugin disable productivity --scope project
```

Si alguno no está instalado:

```powershell
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex --scope project
```

`--scope project` escribe en `.claude/settings.json`: la configuración queda versionada con el repo.

### MCP global: codebase-memory-mcp

Indexa el código en un grafo consultable (no es un plugin). Convive con claude-mem: uno recuerda el código y el otro las sesiones (ver `CLAUDE.md` §3).

```powershell
npm install -g codebase-memory-mcp@0.11.0
codebase-memory-mcp install -y --clients=claude   # solo Claude Code; sin --clients toca todos los clientes detectados
claude mcp list                                   # debe mostrar codebase-memory-mcp ... Connected
```

Si el `npm install` falla con `ETIMEDOUT`, es Windows Defender analizando el `.exe` en su primera ejecución: repetir el comando. Quitar: `codebase-memory-mcp uninstall -y`.

## 3. Codex

```powershell
npm install -g @openai/codex   # solo si `codex --version` falla
codex login                    # cuenta de ChatGPT
codex login status
```

Dentro de Claude Code: `/codex:setup`. Debe reportar el CLI listo. **No actives el review gate** todavía (consume límites en cada turno).

## 4. Verificar que todo está listo

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verificar-entorno.ps1
```

Termina en `LISTO` (exit 0) o lista cada `[FALTA]` con el comando para corregirlo. Pega la salida completa en el chat.

Prueba de humo dentro de Claude Code (en el repo):

1. `/skills` → aparecen las 4 skills del proyecto y las de agent-skills; **no** aparecen las de superpowers.
2. `/codex:setup` → CLI listo y autenticado.
3. Pide: *"usa ui-ux-pro-max para proponer el sistema de diseño de SIGEM"* → debe ejecutar `search.py` sin errores.
4. Pide: *"resume las reglas críticas de AGENTS.md"* → confirma que leyó AGENTS.md vía CLAUDE.md.

Los cuatro en verde = SIGEM-001 (parte agentes) terminado.
