"""Audit logging helper."""
from .models import AuditLog


def log_audit(user, action, model_name='', object_id='', object_repr='', message='', request=None):
    ip = None
    if request:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')) or None
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else '',
        object_repr=object_repr[:255] if object_repr else '',
        message=message,
        ip_address=ip,
    )
