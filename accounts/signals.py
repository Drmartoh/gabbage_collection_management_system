"""Audit log on login."""
from django.contrib.auth.signals import user_logged_in

def on_login(sender, request, user, **kwargs):
    from .utils import log_audit
    log_audit(user, 'login', message=f'User {user.username} logged in', request=request)

user_logged_in.connect(on_login)
