@echo off
setlocal ENABLEDELAYEDEXPANSION

REM 0) Aller a la racine du script
cd /d "%~dp0"

REM 1) Creer le venv si absent (ou si parametre "recreate")
if /I "%~1"=="recreate" (
    echo [INFO] Suppression du venv existant...
    rmdir /s /q ".venv" 2>nul
)

if not exist ".venv" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv .venv || (echo [ERREUR] Echec creation venv & exit /b 1)
)

REM 2) Choisir l’interpreteur du venv (chemin résolu depuis le dossier du script)
set "PYVENV=%~dp0.venv\Scripts\python.exe"
if not exist "%PYVENV%" (
    echo [ERREUR] Interpreteur venv introuvable: %PYVENV%
    exit /b 1
)

REM 3) Mettre pip a jour et installer les dependances
"%PYVENV%" -m pip install --upgrade pip
if exist "requirements.txt" (
    "%PYVENV%" -m pip install -r requirements.txt || (echo [ERREUR] Echec pip install -r requirements.txt & exit /b 1)
) else (
    echo [AVERTISSEMENT] requirements.txt introuvable, on continue...
)

REM 4) Fixer Streamlit headless + port
set "STREAMLIT_SERVER_PORT=8501"
set "STREAMLIT_SERVER_HEADLESS=true"

REM 5) Lancer Streamlit en arrière-plan et loguer la sortie
start "" "%PYVENV%" -m streamlit run app.py --server.port=%STREAMLIT_SERVER_PORT% --server.headless=true 1>run.log 2>&1

REM 6) Attendre un peu puis ouvrir le navigateur
timeout /t 3 >nul
start "" http://localhost:%STREAMLIT_SERVER_PORT%

endlocal