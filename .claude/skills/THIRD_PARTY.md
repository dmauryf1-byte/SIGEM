# Skills de terceros vendorizadas en SIGEM

Copiadas tal cual del commit indicado, revisadas antes de incluirlas (scripts sin acceso a red ni ejecución externa en el flujo usado). Todas MIT; cada carpeta conserva su `LICENSE`.

| Skill | Origen | Commit | Cambios locales |
|---|---|---|---|
| `ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill (`.claude/skills/ui-ux-pro-max`) | `477bcb2` | Rutas `${CLAUDE_PLUGIN_ROOT}/.claude/skills/` → `.claude/skills/`; eliminados `tests/` |
| `redesign-existing-projects` | Leonxlnx/taste-skill (`skills/redesign-skill`) | `ce26fc2` | Ninguno |
| `verification-before-completion` | obra/superpowers (`skills/verification-before-completion`) | `8ca22db` | Ninguno |
| `receiving-code-review` | obra/superpowers (`skills/receiving-code-review`) | `8ca22db` | Ninguno |

**Por qué vendorizadas y no como plugin:** Claude Code no permite desactivar skills sueltas de un plugin (`skillOverrides` no aplica a plugins). Instalar el plugin completo traería skills duplicadas o que piden APIs de pago (Gemini en `design`).

**Actualizar:** volver a copiar desde el upstream, revisar el diff completo y cambiar el commit en esta tabla. Nunca actualizar sin leer el diff.
