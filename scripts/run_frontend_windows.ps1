# scripts/run_frontend_windows.ps1
# Lance l'interface Gradio NURU en natif sous Windows,
# via l'environnement virtuel venv_win (voir scripts\setup_windows.ps1).
#
# Usage : powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = "$ProjectRoot\venv_win\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "venv_win introuvable. Lancez d'abord : powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1"
    exit 1
}

# API_URL fixe explicitement, independamment de toute valeur (perimee) dans .env
$env:API_URL = "http://localhost:8080"
$env:GRADIO_PORT = "7860"

# Meme raison que run_backend_windows.ps1 : sortie UTF-8 forcee pour les emojis.
$env:PYTHONUTF8 = "1"

Write-Output "========================================"
Write-Output "NURU - Frontend Gradio (port $($env:GRADIO_PORT))"
Write-Output "API_URL = $($env:API_URL)"
Write-Output "========================================"
Write-Output "Rappel : l'API backend doit deja tourner (scripts\run_backend_windows.ps1)"
Write-Output "========================================"

& $VenvPython -m frontend.gradio_app
exit $LASTEXITCODE
