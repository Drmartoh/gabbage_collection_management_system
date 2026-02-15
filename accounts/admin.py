from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Role, User, AuditLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display', 'is_read_only')
    list_filter = ('is_read_only',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('username',)
    filter_horizontal = ()
    fieldsets = BaseUserAdmin.fieldsets + (
        ('GCMS', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('GCMS', {'fields': ('role', 'phone')}),
    )

    def response_change(self, request, obj):
        """If the user just assigned themselves a role, send them to the GCMS dashboard."""
        if obj.pk == request.user.pk and obj.role_id:
            return HttpResponseRedirect(reverse('accounts:dashboard_redirect'))
        return super().response_change(request, obj)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_repr', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'message', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'message', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'
