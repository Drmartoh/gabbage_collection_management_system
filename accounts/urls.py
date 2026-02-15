from django.urls import path, reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

def root_redirect(request):
    """Send / to login or dashboard."""
    if request.user.is_authenticated and request.user.role:
        return redirect('accounts:dashboard_redirect')
    return redirect('accounts:login')

urlpatterns = [
    path('', root_redirect),
    path('login/', views.GCMSLoginView.as_view(), name='login'),
    path('logout/', views.GCMSLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('pending-role/', views.pending_role, name='pending_role'),
    path('password-reset/', views.GCMSPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]
