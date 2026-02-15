"""Role-based redirect and read-only enforcement."""
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from .constants import ADMIN_ROLES, COUNTY_READ_ONLY


class RoleRequiredMiddleware(MiddlewareMixin):
    """
    Redirect authenticated users without a role to a "pending role" page.
    Optionally block POST/PUT/DELETE for read-only (County Officer) on sensitive URLs.
    """
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        if not request.user.role:
            path = request.path.rstrip('/') or '/'
            if path.startswith('/admin'):
                return None
            allowed = ('', '/', '/login', '/logout', '/pending-role', '/dashboard',
                       '/password-reset', '/password-reset/done', '/password-reset/complete')
            if path in allowed or path.startswith('/password-reset/'):
                return None
            return redirect('accounts:pending_role')
        return None
