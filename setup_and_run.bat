@echo off
cd /d "%~dp0"
set DJANGO_SUPERUSER_USERNAME=admin
set DJANGO_SUPERUSER_EMAIL=admin@example.com
set DJANGO_SUPERUSER_PASSWORD=adminpass123

echo [1/4] Resetting database and running migrations...
python manage.py reset_db --noinput
if errorlevel 1 exit /b 1

echo [2/4] Seeding data...
python manage.py seed_gcms
if errorlevel 1 exit /b 1

echo [3/4] Creating superuser (admin / adminpass123)...
python manage.py createsuperuser --noinput 2>nul
if errorlevel 1 (
  echo Superuser may already exist - continuing...
)

echo [4/4] Starting server at http://127.0.0.1:8000/
echo Login: admin / adminpass123
echo Then in Admin assign yourself a Role (e.g. Super Admin).
echo.
python manage.py runserver
