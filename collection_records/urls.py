from django.urls import path
from . import views

# Keep app_name so URLs stay as collections:...
app_name = 'collections'

urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='assignment_list'),
    path('add/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_edit'),
    path('<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('collector/', views.collector_dashboard, name='collector_dashboard'),
    path('record/<int:record_id>/log/', views.log_collection, name='log_collection'),
    path('record/<int:record_id>/verify/', views.verify_collection, name='verify_collection'),
    path('labourers/', views.LabourerListView.as_view(), name='labourer_list'),
    path('labourers/add/', views.LabourerCreateView.as_view(), name='labourer_create'),
    path('labourers/<int:pk>/edit/', views.LabourerUpdateView.as_view(), name='labourer_edit'),
    path('labourers/<int:pk>/delete/', views.LabourerDeleteView.as_view(), name='labourer_delete'),
    path('labourer-rotation/', views.LabourerRotationListView.as_view(), name='labourer_rotation_list'),
    path('labourer-rotation/add/', views.LabourerRotationCreateView.as_view(), name='labourer_rotation_create'),
    path('labourer-rotation/<int:pk>/edit/', views.LabourerRotationUpdateView.as_view(), name='labourer_rotation_edit'),
    path('garbage-log/', views.GarbageCollectionLogListView.as_view(), name='garbage_log_list'),
    path('garbage-log/add/', views.GarbageCollectionLogCreateView.as_view(), name='garbage_log_create'),
]
