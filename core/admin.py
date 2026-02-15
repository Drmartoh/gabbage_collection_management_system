from django.contrib import admin
from .models import Ward, Zone, Route, Cart, SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'description', 'updated_at')
    search_fields = ('key', 'description')
    list_editable = ()  # edit via list or form

    def value_preview(self, obj):
        if not obj.value:
            return '(empty)'
        if len(obj.value) > 50:
            return obj.value[:47] + '...'
        return obj.value
    value_preview.short_description = 'Value'


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'county', 'code')


class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward', 'code', 'is_active')
    list_filter = ('ward', 'is_active')
    search_fields = ('name', 'code')


class RouteInline(admin.TabularInline):
    model = Route
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'code', 'day_of_week', 'is_active')
    list_filter = ('zone', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('code', 'route', 'status', 'updated_at')
    list_filter = ('status', 'route')
    search_fields = ('code',)
