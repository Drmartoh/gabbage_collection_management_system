"""Notifications: list for current user."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification


@login_required
def notification_list(request):
    """List current user's notifications."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:100]
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def notification_mark_read(request, pk):
    """Mark a notification as read and optionally redirect to link."""
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    if n.link:
        return redirect(n.link)
    return redirect('notifications:notification_list')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read for the current user."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    from django.contrib import messages
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:notification_list')
