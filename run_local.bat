@echo off
cd /d "%~dp0"

REM Use venv Python if it exists
if exist "venv\Scripts\python.exe" (
  set PY=venv\Scripts\python.exe
) else (
  set PY=python
)

echo Applying migrations...
"%PY%" manage.py migrate --noinput
echo Seeding data (roles, ward, sample landlord, billing)...
"%PY%" manage.py seed_gcms
echo.
echo If you need a login account, run: "%PY%" manage.py createsuperuser
echo.
echo Starting server at http://127.0.0.1:8000/
echo Press Ctrl+C to stop.
echo.
"%PY%" manage.py runserver
pause
