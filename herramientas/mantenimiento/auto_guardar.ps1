# auto_guardar.ps1 — Ejecutado automáticamente por Windows Task Scheduler
# Hace commit + push si hay cambios. Sin ventanas, sin intervención.

# El script vive en herramientas\mantenimiento: el repositorio esta dos niveles arriba
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Definition))
Set-Location $repo

$cambios = git status --porcelain 2>$null
if ($cambios) {
    $fecha = Get-Date -Format "yyyy-MM-dd HH:mm"
    git add -A 2>$null
    git commit -m "auto: $fecha" 2>$null
    git push origin main 2>$null
}
