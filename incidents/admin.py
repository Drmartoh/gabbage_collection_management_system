from django.contrib import admin
from .models import IncidentReport, IncidentPhoto


class IncidentPhotoInline(admin.TabularInline):
    model = IncidentPhoto
    extra = 0


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'property', 'severity', 'status', 'reported_by', 'reported_at')
    list_filter = ('severity', 'status')
    search_fields = ('title', 'description')
    inlines = [IncidentPhotoInline]


@admin.register(IncidentPhoto)
class IncidentPhotoAdmin(admin.ModelAdmin):
    list_display = ('incident', 'caption', 'uploaded_at')
