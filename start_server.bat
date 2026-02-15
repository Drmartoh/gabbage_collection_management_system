@echo off
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
  set PY=venv\Scripts\python.exe
) else (
  set PY=python
)

echo Starting GCMS at http://127.0.0.1:8000/
echo Press Ctrl+C to stop.
echo.
"%PY%" manage.py runserver
pause
