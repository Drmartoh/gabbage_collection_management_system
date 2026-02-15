from django.urls import path
from . import views
from . import views_audit
app_name = 'reports'
urlpatterns = [
    path('county/', views.county_dashboard, name='county_dashboard'),
    path('audit/', views_audit.audit_log_list, name='audit_log'),
    path('', views.export_menu, name='export_menu'),
    path('export/collections-pdf/', views.export_collections_pdf, name='export_collections_pdf'),
    path('export/billing-excel/', views.export_billing_excel, name='export_billing_excel'),
    path('export/incidents-excel/', views.export_incidents_excel, name='export_incidents_excel'),
]
