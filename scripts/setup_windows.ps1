# scripts/setup_windows.ps1
# Prepare un environnement Python Windows pour NURU (le venv/ livre dans le zip
# est un environnement Linux, inutilisable sous Windows).
#
# Usage : powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Output "========================================"
Write-Output "NURU - Preparation de l'environnement Windows"
Write-Output "========================================"

# 1. Verifier Python
# Cette machine peut avoir plusieurs Python installes (3.12/3.14/3.15...) ; la
# commande "python" nue resout de facon imprevisible selon le shell/PATH. On
# epingle explicitement 3.12 (version validee pour l'execution native Windows ;
# les images Docker utilisent Python 3.11)
# via le lanceur officiel "py", avec repli sur "python" si "py" est absent.
Write-Output "`n[1/4] Verification de Python..."
$PyLauncher = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyVersions = & py -0p 2>&1
    if ($pyVersions -match "3\.12") {
        $PyLauncher = @("py", "-3.12")
    }
}
if (-not $PyLauncher) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Output "  AVERTISSEMENT : Python 3.12 introuvable via 'py -0p'. Repli sur 'python' (verifiez sa version)."
        $PyLauncher = @("python")
    } else {
        Write-Error "Aucun interpreteur Python trouve (ni 'py -3.12', ni 'python'). Installez Python 3.12."
        exit 1
    }
}
$pythonVersion = & $PyLauncher[0] $PyLauncher[1..($PyLauncher.Length-1)] --version 2>&1
Write-Output "  OK  $pythonVersion (via $($PyLauncher -join ' '))"

# 2. Creer venv_win s'il n'existe pas
Write-Output "`n[2/4] Environnement virtuel (venv_win)..."
if (Test-Path "$ProjectRoot\venv_win") {
    Write-Output "  INFO venv_win existe deja, reutilisation."
} else {
    & $PyLauncher[0] $PyLauncher[1..($PyLauncher.Length-1)] -m venv venv_win
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Echec de la creation de venv_win."
        exit 1
    }
    Write-Output "  OK  venv_win cree."
}

$VenvPython = "$ProjectRoot\venv_win\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "python.exe introuvable dans venv_win\Scripts. Environnement virtuel corrompu."
    exit 1
}

# 3. Installer les dependances
Write-Output "`n[3/4] Installation des dependances (requirements.txt)..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Error "Echec de la mise a jour de pip."; exit 1 }

& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Echec de l'installation de requirements.txt. Voir le message pip ci-dessus."
    exit 1
}
Write-Output "  OK  Dependances installees."

# 4. Verifier les imports principaux
Write-Output "`n[4/4] Verification des imports principaux..."
$checkScript = @"
import importlib
mods = ['fastapi','uvicorn','langgraph','langchain','sqlalchemy','pydantic','qdrant_client','sympy','gradio','ollama','psycopg','dotenv']
missing = []
for m in mods:
    try:
        importlib.import_module(m)
        print('  OK  ' + m)
    except ImportError as e:
        print('  MANQUANT ' + m + ' - ' + str(e))
        missing.append(m)
if missing:
    raise SystemExit(1)
"@
$checkScript | & $VenvPython -
if ($LASTEXITCODE -ne 0) {
    Write-Error "Certains modules ne s'importent pas correctement. Voir le detail ci-dessus."
    exit 1
}

Write-Output "`n========================================"
Write-Output "Environnement pret."
Write-Output "========================================"
Write-Output "Commandes de lancement :"
Write-Output "  powershell -ExecutionPolicy Bypass -File scripts\run_backend_windows.ps1"
Write-Output "  powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1"
Write-Output "========================================"
