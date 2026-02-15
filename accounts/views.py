"""Authentication and dashboard redirect views."""
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .decorators import admin_dashboard_required, county_or_admin_required
from .models import AuditLog
from .utils import log_audit


class GCMSLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        result = super().form_valid(form)
        if self.request.user.is_authenticated:
            log_audit(
                self.request.user,
                'login',
                message=f'User {self.request.user.get_display_name()} logged in',
                request=self.request,
            )
        return result


class GCMSPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class GCMSLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post', 'head']

    def get_redirect_url(self):
        """Redirect to login; ignore empty or invalid ?next=. Only allow relative paths (no open redirect)."""
        next_url = self.request.GET.get(self.redirect_field_name, '').strip()
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            from django.shortcuts import resolve_url
            return resolve_url(next_url)
        return str(self.next_page)

    def get(self, request, *args, **kwargs):
        """Allow GET so logout links work without a form."""
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.get_redirect_url())


@login_required
def dashboard_redirect(request):
    """Send user to role-appropriate dashboard."""
    if not request.user.role:
        return redirect('accounts:pending_role')
    role_name = request.user.role.name
    if role_name in ('super_admin', 'operations_admin', 'supervisor'):
        return redirect('core:admin_dashboard')
    if role_name == 'county_officer':
        return redirect('reports:county_dashboard')
    if role_name == 'collector':
        return redirect('collections:collector_dashboard')
    if role_name == 'landlord':
        return redirect('properties:landlord_dashboard')
    if role_name == 'casual_labourer':
        return redirect('collections:garbage_log_list')
    return redirect('accounts:pending_role')


@login_required
def pending_role(request):
    """Shown when user has no role assigned."""
    return render(request, 'accounts/pending_role.html')


@admin_dashboard_required
def admin_dashboard(request):
    """AGCBO admin dashboard - redirect to core dashboard."""
    return redirect('core:admin_dashboard')


@county_or_admin_required
def county_dashboard(request):
    """County officer read-only dashboard."""
    return redirect('reports:county_dashboard')
