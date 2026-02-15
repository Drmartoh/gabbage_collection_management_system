"""GCMS URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import admin_site  # noqa: F401 - customizes admin branding

handler404 = 'gcms.views.page_not_found'
handler500 = 'gcms.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('core/', include('core.urls')),
    path('properties/', include('properties.urls')),
    path('collections/', include('collection_records.urls')),
    path('billing/', include('billing.urls')),
    path('incidents/', include('incidents.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
