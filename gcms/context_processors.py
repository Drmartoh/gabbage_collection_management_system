"""Global context processors for GCMS."""
from django.conf import settings


def gcms_settings(request):
    """Expose GCMS settings to templates (non-sensitive only)."""
    return {
        'GCMS_RATE_PER_TENANT': getattr(settings, 'GCMS_RATE_PER_TENANT_MONTHLY', 100),
        'GCMS_SITE_NAME': 'Garbage Collection Management System',
        'GCMS_WARD': 'Karai Ward',
        'GCMS_COUNTY': 'Kiambu County',
        'HERE_API_KEY': getattr(settings, 'HERE_API_KEY', '') or '',
    }


def gcms_notification_count(request):
    """Expose unread notification count for authenticated users."""
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            count = Notification.objects.filter(user=request.user, is_read=False).count()
            return {'gcms_unread_notifications': min(count, 99)}
        except Exception:
            pass
    return {'gcms_unread_notifications': 0}


def gcms_walkthrough(request):
    """Expose in-app training state: welcome tour and per-page tips."""
    try:
        from core.models import SystemSetting
        from core.walkthrough import get_tip_for_view
        enabled = SystemSetting.get_value('walkthrough_enabled', 'true').lower() in ('true', '1', 'yes')
    except Exception:
        enabled = True
        get_tip_for_view = lambda v: None

    ctx = {
        'gcms_walkthrough_enabled': enabled,
        'gcms_show_welcome_tour': False,
        'gcms_show_walkthrough_tip': False,
        'gcms_walkthrough_tip': None,
        'gcms_walkthrough_page_slug': None,
    }
    if not request.user.is_authenticated or not enabled:
        return ctx

    user = request.user
    ctx['gcms_show_welcome_tour'] = not getattr(user, 'first_login_tour_done', False)

    view_name = None
    if getattr(request, 'resolver_match', None):
        view_name = getattr(request.resolver_match, 'view_name', None)
    tip = get_tip_for_view(view_name) if view_name else None
    if tip:
        slug = tip.get('slug')
        seen = getattr(user, 'walkthrough_page_tips_seen', None) or []
        if slug and slug not in seen:
            ctx['gcms_show_walkthrough_tip'] = True
            ctx['gcms_walkthrough_tip'] = tip
            ctx['gcms_walkthrough_page_slug'] = slug
    return ctx
