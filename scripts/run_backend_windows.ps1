# scripts/run_backend_windows.ps1
# Lance l'API NURU (FastAPI + agents LangGraph) en natif sous Windows,
# via l'environnement virtuel venv_win (voir scripts\setup_windows.ps1).
#
# Usage : powershell -ExecutionPolicy Bypass -File scripts\run_backend_windows.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = "$ProjectRoot\venv_win\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "venv_win introuvable. Lancez d'abord : powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1"
    exit 1
}

# Charger .env dans l'environnement du process courant
$EnvFile = "$ProjectRoot\.env"
if (Test-Path $EnvFile) {
    Write-Output "Chargement de .env..."
    Get-Content $EnvFile | Where-Object { $_ -match '=' -and $_ -notmatch '^\s*#' } | ForEach-Object {
        $k, $v = $_ -split '=', 2
        $k = $k.Trim()
        $v = $v.Trim()
        if ($k) {
            Set-Item -Path "Env:$k" -Value $v
        }
    }
} else {
    Write-Output "AVERTISSEMENT : .env introuvable. Copiez .env.example en .env avant de continuer."
}

# Port de l'API : force explicitement 8080, quelle que soit la valeur de .env
$env:PORT = "8080"

# La console Windows (codepage cp1252 par defaut) ne supporte pas les emojis
# utilises par les print() du code (ex: "NURU" avec icones). PYTHONUTF8 force
# une sortie UTF-8, sans toucher au code source.
$env:PYTHONUTF8 = "1"

Write-Output "========================================"
Write-Output "NURU - API backend (port $($env:PORT))"
Write-Output "========================================"
Write-Output "Rappel : Postgres/Qdrant doivent deja tourner (docker compose up -d postgres qdrant)"
Write-Output "Rappel : Ollama natif doit deja tourner (ollama serve, ou deja actif en service)"
Write-Output "========================================"

& $VenvPython -m backend.app.api.main
exit $LASTEXITCODE
