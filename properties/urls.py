from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.LandlordListView.as_view(), name='landlord_list'),
    path('tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path('add/', views.LandlordCreateView.as_view(), name='landlord_create'),
    path('<int:pk>/', views.LandlordDetailView.as_view(), name='landlord_detail'),
    path('<int:pk>/edit/', views.LandlordUpdateView.as_view(), name='landlord_edit'),
    path('<int:pk>/delete/', views.LandlordDeleteView.as_view(), name='landlord_delete'),
    path('landlord/<int:landlord_id>/property/add/', views.PropertyCreateView.as_view(), name='property_create'),
    path('property/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('property/<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('property/<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
    path('property/<int:property_id>/tenant/add/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('tenant/<int:pk>/edit/', views.TenantUpdateView.as_view(), name='tenant_edit'),
    path('tenant/<int:pk>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    path('my/', views.landlord_dashboard, name='landlord_dashboard'),
]
