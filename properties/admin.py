from django.contrib import admin
from .models import Landlord, Property, Tenant, PropertyCollectionDay


class PropertyInline(admin.TabularInline):
    model = Property
    extra = 0
    show_change_link = True


@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('full_name', 'phone', 'email')
    inlines = [PropertyInline]


class TenantInline(admin.TabularInline):
    model = Tenant
    extra = 0


class PropertyCollectionDayInline(admin.TabularInline):
    model = PropertyCollectionDay
    extra = 0
    max_num = 7


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'landlord', 'route', 'plot_number', 'is_active')
    list_filter = ('landlord', 'route', 'is_active')
    search_fields = ('name', 'plot_number', 'physical_address')
    inlines = [TenantInline, PropertyCollectionDayInline]


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'property', 'phone', 'is_active')
    list_filter = ('property__landlord', 'is_active')
    search_fields = ('full_name', 'phone')
