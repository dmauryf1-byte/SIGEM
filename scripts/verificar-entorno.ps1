# SIGEM-001 - Verifica que el entorno y los agentes esten listos. Solo lee: no instala ni cambia nada.
# Uso (desde la raiz del repo):  powershell -ExecutionPolicy Bypass -File scripts\verificar-entorno.ps1

$fallos = 0

function Check([string]$nombre, [scriptblock]$cmd, [switch]$Opcional) {
    $global:LASTEXITCODE = 0
    try {
        $out = (& $cmd 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) { throw $out }
        Write-Host ("[OK]    {0,-18} {1}" -f $nombre, ($out -split "`n")[0]) -ForegroundColor Green
    } catch {
        $msg = ("$($_.Exception.Message)" -split "`n")[0]
        if ($Opcional) {
            Write-Host ("[INFO]  {0,-18} no disponible (opcional)" -f $nombre) -ForegroundColor Yellow
        } else {
            Write-Host ("[FALTA] {0,-18} {1}" -f $nombre, $msg) -ForegroundColor Red
            $script:fallos++
        }
    }
}

Write-Host "`n== Herramientas ==" -ForegroundColor Cyan
Check "Python"         { python --version }
Check "uv"             { uv --version }
Check "Node.js"        { node --version }
Check "npm"            { npm --version }
Check "Git"            { git --version }
Check "Docker"         { docker --version }
Check "Docker Compose" { docker compose version }
Check "Docker daemon"  { docker info --format "{{.ServerVersion}}" }
Check "VS Code"        { code --version }
Check "MySQL local"    { mysql --version } -Opcional   # MySQL corre en Docker; el cliente local es opcional
Check "Claude Code"    { claude --version }
Check "Codex CLI"      { codex --version }
Check "Codex login"    { codex login status }
Check "codebase-memory" { codebase-memory-mcp --version } -Opcional   # MCP de grafo de codigo (ver CLAUDE.md, seccion 3)

Write-Host "`n== Plugins de Claude Code ==" -ForegroundColor Cyan
try {
    $plugins = claude plugin list --json 2>$null | ConvertFrom-Json
} catch {
    $plugins = @()
    Write-Host "[FALTA] No se pudo leer 'claude plugin list --json'" -ForegroundColor Red
    $fallos++
}
$plugins | ForEach-Object { Write-Host ("        {0,-45} enabled={1}" -f $_.id, $_.enabled) }

function Find([string]$nombre) { $plugins | Where-Object { $_.id -like "$nombre@*" -or $_.installPath -like "*$nombre*" } }

foreach ($p in "agent-skills", "codex", "ponytail") {
    $hit = Find $p | Where-Object { $_.enabled }
    if ($hit) { Write-Host "[OK]    $p activo" -ForegroundColor Green }
    else      { Write-Host "[FALTA] $p no esta instalado o esta desactivado" -ForegroundColor Red; $fallos++ }
}
foreach ($p in "superpowers", "claude-mem-cowork", "frontend-design", "productivity") {
    $hit = Find $p | Where-Object { $_.enabled }
    if ($hit) {
        Write-Host "[FALTA] $p sigue activo. Ejecuta:  claude plugin disable $($hit[0].id) --scope project" -ForegroundColor Red
        $fallos++
    } else {
        Write-Host "[OK]    $p desactivado" -ForegroundColor Green
    }
}
$plugins | Where-Object { $_.errors } | ForEach-Object {
    Write-Host "[FALTA] $($_.id) tiene errores de carga: $($_.errors -join '; ')" -ForegroundColor Red; $fallos++
}

Write-Host "`n== Skills del proyecto (.claude/skills) ==" -ForegroundColor Cyan
foreach ($s in "ui-ux-pro-max", "redesign-existing-projects", "verification-before-completion", "receiving-code-review") {
    if (Test-Path ".claude/skills/$s/SKILL.md") { Write-Host "[OK]    $s" -ForegroundColor Green }
    else { Write-Host "[FALTA] $s (ejecuta el script desde la raiz del repo)" -ForegroundColor Red; $fallos++ }
}
Check "ui-ux-pro-max"  { python .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain style -n 1 }

Write-Host "`n== Archivos de reglas ==" -ForegroundColor Cyan
foreach ($f in "AGENTS.md", "CLAUDE.md") {
    if (Test-Path $f) { Write-Host "[OK]    $f" -ForegroundColor Green }
    else { Write-Host "[FALTA] $f" -ForegroundColor Red; $fallos++ }
}

Write-Host ""
if ($fallos -eq 0) { Write-Host "LISTO: entorno verificado. Siguiente: /codex:setup dentro de Claude Code." -ForegroundColor Green; exit 0 }
else { Write-Host "$fallos verificacion(es) fallaron. Pega esta salida completa en el chat." -ForegroundColor Red; exit 1 }
