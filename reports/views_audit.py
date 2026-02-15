"""Audit log viewer for admins."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from accounts.decorators import admin_dashboard_required
from accounts.models import AuditLog


@admin_dashboard_required
def audit_log_list(request):
    """List recent audit log entries."""
    qs = AuditLog.objects.select_related('user').order_by('-created_at')
    paginator = Paginator(qs, 50)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'reports/audit_log.html', {'page_obj': page_obj})
