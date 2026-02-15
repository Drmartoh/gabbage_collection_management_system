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

Create a `.env` file in the project root (`~/gcms_project/.env`):

```bash
DEBUG=False
SECRET_KEY=your-long-random-secret-key-here
ALLOWED_HOSTS=yourusername.pythonanywhere.com
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

- In the PythonAnywhere **Web** tab:
  - **WSGI configuration file**: edit it and set the path to your project and virtualenv, for example:

```python
import os
import sys
path = '/home/yourusername/gcms_project'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'gcms.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

  - **Virtualenv**: set to `/home/yourusername/gcms_project/venv`
  - **Static files** (optional; Whitenoise also serves static):
    - URL: `/static/`
    - Directory: `/home/yourusername/gcms_project/staticfiles`
  - **Static files** for uploads:
    - URL: `/media/`
    - Directory: `/home/yourusername/gcms_project/media`

## 6. Reload and test

- Click **Reload** for your web app.
- Open `https://yourusername.pythonanywhere.com/`, log in, and assign yourself a role in Django Admin (`/admin/`).

## 7. HTTPS / cookies (production)

With `DEBUG=False`, the app sets secure cookies by default. If you need to force them on PA, add to `.env`:

```bash
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```
