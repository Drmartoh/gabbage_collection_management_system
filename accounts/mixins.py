"""Mixin for class-based views requiring admin dashboard access."""
from django.core.exceptions import PermissionDenied
from .constants import ADMIN_ROLES


class AdminDashboardRequiredMixin:
    """Require Super Admin, Operations Admin, or Supervisor."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.role:
            raise PermissionDenied('No role assigned.')
        if request.user.role.name not in ADMIN_ROLES:
            raise PermissionDenied('Insufficient permissions.')
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(self.request.get_full_path())
