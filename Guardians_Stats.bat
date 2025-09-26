@echo off
setlocal

REM 1) Créer/activer l'environnement virtuel local
if not exist .venv (
  python -m venv .venv
  call .\.venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
) else (
  call .\.venv\Scripts\activate
)

REM 2) Choisir le port de Streamlit
set "STREAMLIT_SERVER_PORT=8501"

REM 3) Empêcher Streamlit d'ouvrir le navigateur automatiquement
set "BROWSER=none"

REM 4) Lancer Streamlit en arrière-plan avec le port fixé
start "" cmd /c "python -m streamlit run app.py --server.headless=true --server.port=%STREAMLIT_SERVER_PORT%"

REM 5) Attendre un peu que le serveur démarre (ajuster si besoin)
timeout /t 3 >nul

REM 6) Ouvrir UNE SEULE FOIS le navigateur
start "" http://localhost:%STREAMLIT_SERVER_PORT%

endlocal
