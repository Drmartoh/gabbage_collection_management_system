from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('properties-map/', views.properties_heatmap, name='properties_heatmap'),
    path('ward-map/', views.ward_map, name='ward_map'),
    path('settings/', views.gcms_settings_page, name='gcms_settings'),
    path('wards/', views.WardListView.as_view(), name='ward_list'),
    path('wards/add/', views.WardCreateView.as_view(), name='ward_create'),
    path('wards/<int:pk>/edit/', views.WardUpdateView.as_view(), name='ward_edit'),
    path('wards/<int:pk>/delete/', views.WardDeleteView.as_view(), name='ward_delete'),
    path('zones/', views.ZoneListView.as_view(), name='zone_list'),
    path('zones/add/', views.ZoneCreateView.as_view(), name='zone_create'),
    path('zones/<int:pk>/edit/', views.ZoneUpdateView.as_view(), name='zone_edit'),
    path('zones/<int:pk>/delete/', views.ZoneDeleteView.as_view(), name='zone_delete'),
    path('routes/', views.RouteListView.as_view(), name='route_list'),
    path('routes/add/', views.RouteCreateView.as_view(), name='route_create'),
    path('routes/<int:pk>/edit/', views.RouteUpdateView.as_view(), name='route_edit'),
    path('routes/<int:pk>/map/', views.route_map, name='route_map'),
    path('routes/<int:pk>/delete/', views.RouteDeleteView.as_view(), name='route_delete'),
    path('carts/', views.CartListView.as_view(), name='cart_list'),
    path('carts/add/', views.CartCreateView.as_view(), name='cart_create'),
    path('carts/<int:pk>/edit/', views.CartUpdateView.as_view(), name='cart_edit'),
    path('carts/<int:pk>/delete/', views.CartDeleteView.as_view(), name='cart_delete'),
    path('walkthrough/mark-welcome-done/', views.walkthrough_mark_welcome_done, name='walkthrough_mark_welcome_done'),
    path('walkthrough/mark-page-seen/', views.walkthrough_mark_page_seen, name='walkthrough_mark_page_seen'),
]
