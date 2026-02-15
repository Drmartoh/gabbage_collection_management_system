from django.contrib import admin
from .models import (
    BillingCycle, LandlordBill, PaymentRecord,
    ExpenseType, Expense, LabourerPayment,
)


class LandlordBillInline(admin.TabularInline):
    model = LandlordBill
    extra = 0


@admin.register(BillingCycle)
class BillingCycleAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'is_closed', 'created_at')
    list_filter = ('is_closed',)
    inlines = [LandlordBillInline]


class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0


@admin.register(LandlordBill)
class LandlordBillAdmin(admin.ModelAdmin):
    list_display = ('landlord', 'cycle', 'tenant_count', 'amount', 'amount_paid', 'updated_at')
    list_filter = ('cycle',)
    search_fields = ('landlord__full_name',)
    inlines = [PaymentRecordInline]


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('bill', 'amount', 'method', 'reference', 'paid_at', 'recorded_by')
    list_filter = ('method', 'paid_at')
    search_fields = ('reference',)


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'pay_frequency', 'is_active')
    list_filter = ('pay_frequency', 'is_active')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_type', 'amount', 'due_date', 'vendor', 'paid_at', 'recorded_by')
    list_filter = ('expense_type', 'paid_at')
    search_fields = ('vendor', 'reference', 'notes')
    date_hierarchy = 'due_date'


@admin.register(LabourerPayment)
class LabourerPaymentAdmin(admin.ModelAdmin):
    list_display = ('labourer', 'week_ending_date', 'amount', 'paid_at', 'recorded_by')
    list_filter = ('week_ending_date',)
    search_fields = ('labourer__full_name',)
    date_hierarchy = 'week_ending_date'
