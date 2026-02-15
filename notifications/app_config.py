from pathlib import Path

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Notifications & SMS'
    # Explicit path so Django uses a single canonical location (fixes duplicate
    # path resolution e.g. on PythonAnywhere when .../notifications and ..././notifications are both seen)
    path = Path(__file__).resolve().parent
