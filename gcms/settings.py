"""
GCMS - Garbage Collection Management System
Production-ready settings for Karai Ward, Kiambu County, Kenya.
"""
import os
from pathlib import Path

import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    SECRET_KEY=(str, 'change-me-in-production'),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3'),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
# PythonAnywhere: set ALLOWED_HOSTS=yourusername.pythonanywhere.com (comma-separated if multiple)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    # GCMS apps
    'accounts',
    'core',
    'properties',
    'collection_records',
    'billing',
    'incidents',
    'notifications',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.RoleRequiredMiddleware',
]

ROOT_URLCONF = 'gcms.urls'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard_redirect'
LOGOUT_REDIRECT_URL = 'accounts:login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'gcms.context_processors.gcms_settings',
                'gcms.context_processors.gcms_notification_count',
                'gcms.context_processors.gcms_walkthrough',
            ],
        },
    },
]

WSGI_APPLICATION = 'gcms.wsgi.application'

# Database
DATABASES = {'default': env.db()}

# Custom user
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-ke'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static and media
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
# Avoid manifest errors in development when collectstatic hasn't been run
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG else 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email: use console backend in development so password-reset emails are printed to console
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# In production, set EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Billing
GCMS_RATE_PER_TENANT_MONTHLY = 100  # KES

# SMS (API-ready)
GCMS_SMS_API_URL = env.str('GCMS_SMS_API_URL', default='')
GCMS_SMS_API_KEY = env.str('GCMS_SMS_API_KEY', default='')
GCMS_SMS_SENDER_ID = env.str('GCMS_SMS_SENDER_ID', default='GCMS')

# HERE Maps (maps, geocoding, routing) - set HERE_API_KEY in .env for live maps
HERE_API_KEY = env.str('HERE_API_KEY', default='')

# Custom audit via accounts.AuditLog model

# Session security
SESSION_COOKIE_AGE = 3600 * 8
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
# On PythonAnywhere (HTTPS), these are True when DEBUG=False
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=not DEBUG)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging: file + console, avoid errors when log dir missing
LOG_DIR = BASE_DIR / 'logs'
if not LOG_DIR.exists():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        LOG_DIR = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '[{levelname}] {asctime} {name} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {'level': 'ERROR', 'propagate': True},
        'django.security': {'level': 'ERROR', 'propagate': True},
    },
}
if LOG_DIR:
    LOGGING['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': LOG_DIR / 'gcms.log',
        'formatter': 'verbose',
        'encoding': 'utf-8',
    }
    LOGGING['root']['handlers'] = ['console', 'file']
    # Ensure 500s and security errors are written to file with tracebacks
    LOGGING['loggers']['django.request'] = {
        'level': 'ERROR',
        'handlers': ['console', 'file'],
        'propagate': False,
    }
    LOGGING['loggers']['django.security'] = {
        'level': 'ERROR',
        'handlers': ['console', 'file'],
        'propagate': False,
    }
