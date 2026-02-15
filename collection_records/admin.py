from django.contrib import admin
from .models import (
    RouteAssignment, CollectionRecord,
    CasualLabourer, LabourerZoneRotation, GarbageCollectionLog,
)


class CollectionRecordInline(admin.TabularInline):
    model = CollectionRecord
    extra = 0
    readonly_fields = ('verified_by', 'verified_at')


@admin.register(RouteAssignment)
class RouteAssignmentAdmin(admin.ModelAdmin):
    list_display = ('route', 'collector', 'cart', 'date', 'is_completed', 'updated_at')
    list_filter = ('date', 'is_completed')
    search_fields = ('route__name', 'collector__username')
    inlines = [CollectionRecordInline]


@admin.register(CollectionRecord)
class CollectionRecordAdmin(admin.ModelAdmin):
    list_display = ('property', 'assignment', 'status', 'collected_at', 'verified_by', 'verified_at')
    list_filter = ('status', 'assignment__date')
    search_fields = ('property__name',)
    readonly_fields = ('verified_by', 'verified_at')


@admin.register(CasualLabourer)
class CasualLabourerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'id_number', 'user', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('full_name', 'phone')


@admin.register(LabourerZoneRotation)
class LabourerZoneRotationAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'zone', 'valid_from', 'valid_to', 'assigned_by')
    list_filter = ('zone', 'valid_from')
    search_fields = ('labourer__full_name',)
    date_hierarchy = 'valid_from'


@admin.register(GarbageCollectionLog)
class GarbageCollectionLogAdmin(admin.ModelAdmin):
    list_display = ('collection_date', 'labourer', 'property', 'landlord', 'recorded_by')
    list_filter = ('collection_date', 'zone')
    search_fields = ('property__name', 'labourer__full_name', 'incident_or_dispute')
    date_hierarchy = 'collection_date'
