from django.contrib import admin
from .models import Notification, SMSLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('title', 'message')


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'sent_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('recipient',)
    readonly_fields = ('created_at', 'sent_at')
