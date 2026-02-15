"""Role-based access decorators."""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .constants import ADMIN_ROLES, COUNTY_READ_ONLY


def role_required(*allowed_roles):
    """Require user to have one of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not request.user.role:
                raise PermissionDenied('No role assigned.')
            role_name = request.user.role.name
            if role_name not in allowed_roles:
                raise PermissionDenied('Insufficient permissions.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def admin_dashboard_required(view_func):
    """Allow Super Admin, Operations Admin, Supervisor (AGCBO admins)."""
    return role_required(*ADMIN_ROLES)(view_func)


def county_or_admin_required(view_func):
    """Allow County Officer (read-only) or admin roles."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.role:
            raise PermissionDenied('No role assigned.')
        role_name = request.user.role.name
        if role_name in ADMIN_ROLES or role_name in COUNTY_READ_ONLY:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied('Insufficient permissions.')
    return _wrapped


def write_required(view_func):
    """Block County Officer (read-only) from POST/modify actions."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_read_only:
            raise PermissionDenied('Read-only access.')
        return view_func(request, *args, **kwargs)
    return _wrapped
