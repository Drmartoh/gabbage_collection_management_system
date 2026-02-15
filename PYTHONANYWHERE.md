# Deploying GCMS on PythonAnywhere

## 1. Upload your project

- Clone or upload the `gcms_project` folder to your PythonAnywhere account (e.g. `/home/yourusername/gcms_project`).

## 2. Create a virtualenv

In a Bash console on PythonAnywhere:

```bash
cd ~/gcms_project
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(Use the Python version you selected for your Web app, e.g. 3.10.)

## 3. Environment variables

Create a `.env` file in the project root (e.g. `~/gabbage_collection_management_system/.env` or `~/gcms_project/.env`).

**Generate a SECRET_KEY** (run once, then paste the output into `.env`):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or with Python only (no Django needed yet):

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Example `.env` for **gcmskarai.pythonanywhere.com**:

```bash
DEBUG=False
SECRET_KEY=paste-the-generated-key-here
ALLOWED_HOSTS=gcmskarai.pythonanywhere.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

For MySQL (optional, free tier):

```bash
DATABASE_URL=mysql://yourusername:yourmysqlpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$gcms
```

Install MySQL driver: `pip install mysqlclient` and add to requirements if you use MySQL.

## 4. Database and static files

```bash
source venv/bin/activate
cd ~/gcms_project
python manage.py migrate
python manage.py seed_gcms
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 5. Web app configuration

In the PythonAnywhere **Web** tab, set the following. Replace the project folder name if you used something other than `gabbage_collection_management_system` (e.g. if you cloned into `gcms_project`).

| Field | Value |
|-------|--------|
| **Source code** | `/home/gcmskarai/gabbage_collection_management_system` |
| **Working directory** | `/home/gcmskarai/gabbage_collection_management_system` (same as source; must contain `manage.py`) |
| **WSGI configuration file** | `/var/www/gcmskarai_pythonanywhere_com_wsgi.py` (PA sets this; you only edit its contents) |
| **Virtualenv** | `/home/gcmskarai/.virtualenvs/gcms` (if you used `mkvirtualenv gcms`) or `/home/gcmskarai/gabbage_collection_management_system/venv` (if you used a venv inside the project) |

**Edit the WSGI file** (click the path to open it). Replace the entire file with the following. Using one **resolved** path and setting the working directory avoids the "notifications has multiple filesystem locations" error:

```python
import os
import sys

# Use a single canonical path (no . or ..) so app modules are not seen twice
project_root = os.path.abspath('/home/gcmskarai/django_projects/gabbage_collection_management_system')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gcms.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

If your project is elsewhere (e.g. `/home/gcmskarai/gabbage_collection_management_system`), change the path in the first line to that directory.

**Static files** (in the same Web tab, scroll to "Static files"):
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/gcmskarai/gabbage_collection_management_system/staticfiles` |
| `/media/` | `/home/gcmskarai/gabbage_collection_management_system/media` |

## 6. Reload and test

- Click **Reload** for your web app.
- Open **https://gcmskarai.pythonanywhere.com/** (or your PA URL), log in, and assign yourself a role in Django Admin (`/admin/`).

## 7. HTTPS / cookies (production)

With `DEBUG=False`, the app sets secure cookies by default. If you need to force them on PA, add to `.env`:

```bash
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```
