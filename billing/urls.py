from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.BillListView.as_view(), name='bill_list'),
    path('cycles/', views.BillingCycleListView.as_view(), name='cycle_list'),
    path('cycles/add/', views.BillingCycleCreateView.as_view(), name='cycle_create'),
    path('cycles/<int:pk>/edit/', views.BillingCycleUpdateView.as_view(), name='cycle_edit'),
    path('cycles/<int:cycle_id>/generate/', views.generate_bills, name='generate_bills'),
    path('my/', views.my_bills, name='my_bills'),
    path('bill/<int:bill_id>/pay/', views.record_payment, name='record_payment'),
    path('arrears/', views.arrears_list, name='arrears_list'),
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_edit'),
    path('expenses/<int:pk>/mark-paid/', views.expense_mark_paid, name='expense_mark_paid'),
    path('expense-types/', views.expense_type_list, name='expense_type_list'),
    path('payroll/', views.labourer_payment_list, name='labourer_payment_list'),
    path('payroll/add/', views.LabourerPaymentCreateView.as_view(), name='labourer_payment_add'),
]
