"""Billing: bills, payments, landlord-based KES 100/tenant; arrears, expenses, payroll."""
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django import forms
from django.utils import timezone
from django.db.models import Sum, Q
from accounts.decorators import role_required, admin_dashboard_required
from accounts.mixins import AdminDashboardRequiredMixin
from accounts.constants import LANDLORD
from properties.models import Landlord
from .models import (
    BillingCycle, LandlordBill, PaymentRecord,
    ExpenseType, Expense, LabourerPayment,
)

def get_standard_rate():
    """Default monthly rate per tenant (KES). From SystemSetting, then settings."""
    try:
        from core.models import SystemSetting
        v = SystemSetting.get_value('billing_rate_per_tenant', '')
        if v.isdigit():
            return int(v)
    except Exception:
        pass
    return getattr(settings, 'GCMS_RATE_PER_TENANT_MONTHLY', 100)


class BillListView(LoginRequiredMixin, ListView):
    model = LandlordBill
    template_name = 'billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 30

    def get_queryset(self):
        return LandlordBill.objects.select_related('landlord', 'cycle').order_by('-cycle__year', '-cycle__month', 'landlord')

    def get_context_data(self, **kwargs):
        from django.urls import reverse
        ctx = super().get_context_data(**kwargs)
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Billing'},
        ]
        return ctx


class BillingCycleForm(forms.ModelForm):
    class Meta:
        model = BillingCycle
        fields = ('year', 'month', 'is_closed')
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2030}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BillingCycleListView(AdminDashboardRequiredMixin, LoginRequiredMixin, ListView):
    model = BillingCycle
    template_name = 'billing/cycle_list.html'
    context_object_name = 'cycles'

    def get_queryset(self):
        return BillingCycle.objects.order_by('-year', '-month')


class BillingCycleCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = BillingCycle
    form_class = BillingCycleForm
    template_name = 'billing/cycle_form.html'
    success_url = reverse_lazy('billing:cycle_list')

    def form_valid(self, form):
        messages.success(self.request, 'Billing cycle created. You can generate bills for it from the list.')
        return super().form_valid(form)


class BillingCycleUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = BillingCycle
    form_class = BillingCycleForm
    template_name = 'billing/cycle_form.html'
    context_object_name = 'cycle'
    success_url = reverse_lazy('billing:cycle_list')

    def form_valid(self, form):
        messages.success(self.request, 'Billing cycle updated.')
        return super().form_valid(form)


@admin_dashboard_required
@require_http_methods(['POST'])
def generate_bills(request, cycle_id):
    """Generate or update landlord bills for a billing cycle."""
    from accounts.utils import log_audit

    cycle = get_object_or_404(BillingCycle, pk=cycle_id)
    standard_rate = get_standard_rate()
    count = 0
    for ll in Landlord.objects.filter(is_active=True).prefetch_related('properties__tenants'):
        tenant_count = ll.tenant_count()
        if tenant_count > 0:
            amount = ll.billing_amount(standard_rate)
            bill, created = LandlordBill.objects.get_or_create(
                cycle=cycle,
                landlord=ll,
                defaults={
                    'tenant_count': tenant_count,
                    'amount': amount,
                }
            )
            if not created:
                bill.tenant_count = tenant_count
                bill.amount = amount
                bill.save()
            count += 1
    log_audit(
        request.user,
        'create',
        model_name='LandlordBill',
        object_repr=str(cycle),
        message=f'Generated/updated {count} bills for {cycle}',
        request=request,
    )
    messages.success(request, f'Generated/updated {count} bills for {cycle}.')
    return redirect('billing:bill_list')


@role_required(LANDLORD)
def my_bills(request):
    try:
        profile = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.warning(request, 'No landlord profile.')
        return redirect('accounts:dashboard_redirect')
    bills = LandlordBill.objects.filter(landlord=profile).select_related('cycle').order_by('-cycle__year', '-cycle__month')
    return render(request, 'billing/my_bills.html', {'bills': bills})


@admin_dashboard_required
@require_http_methods(['GET', 'POST'])
def record_payment(request, bill_id):
    """Record a payment against a landlord bill (admin/ops/supervisor)."""
    from accounts.utils import log_audit
    from notifications.models import Notification

    bill = get_object_or_404(LandlordBill, pk=bill_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('method', 'mpesa')
        reference = request.POST.get('reference', '')
        if amount:
            try:
                amount_dec = Decimal(amount)
                if amount_dec <= 0:
                    messages.error(request, 'Amount must be greater than zero.')
                elif amount_dec > bill.balance:
                    messages.error(
                        request,
                        f'Amount (KES {amount_dec:,.0f}) exceeds balance (KES {bill.balance:,.0f}). '
                        'Record partial payment or adjust the bill.',
                    )
                else:
                    PaymentRecord.objects.create(
                        bill=bill,
                        amount=amount_dec,
                        method=method,
                        reference=reference.strip(),
                        recorded_by=request.user,
                    )
                    log_audit(
                        request.user,
                        'create',
                        model_name='PaymentRecord',
                        object_repr=f'KES {amount_dec} for {bill.landlord}',
                        message=f'Payment recorded for {bill.landlord.full_name}',
                        request=request,
                    )
                    if bill.landlord.user_id:
                        Notification.objects.create(
                            user=bill.landlord.user,
                            title='Payment received',
                            message=f'Payment of KES {amount_dec:,.0f} was recorded for bill {bill.cycle}.',
                            link='/billing/my/',
                        )
                    if bill.landlord.phone and bill.landlord.phone.strip():
                        from django.conf import settings
                        if getattr(settings, 'GCMS_SMS_API_URL', None) and getattr(settings, 'GCMS_SMS_API_KEY', None):
                            from notifications.services import send_sms
                            bill.refresh_from_db()
                            msg = f'GCMS: Payment of KES {amount_dec:,.0f} received. Balance: KES {bill.balance:,.0f}.'
                            send_sms(bill.landlord.phone.strip(), msg)
                    messages.success(request, 'Payment recorded successfully.')
                    return redirect('billing:bill_list')
            except Exception:
                messages.error(request, 'Invalid amount.')
        else:
            messages.error(request, 'Please enter an amount.')
    from django.urls import reverse
    return render(request, 'billing/record_payment.html', {
        'bill': bill,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Billing', 'url': reverse('billing:bill_list')},
            {'label': 'Record payment'},
        ],
    })


# --- Arrears (pending landlord bills) ---

@admin_dashboard_required
def arrears_list(request):
    """All landlords with pending balance (arrears)."""
    from django.db.models import F
    bills_with_balance = LandlordBill.objects.filter(
        amount__gt=F('amount_paid')
    ).select_related('landlord', 'cycle').order_by('-cycle__year', '-cycle__month', 'landlord')
    total_arrears = sum((b.amount - b.amount_paid) for b in bills_with_balance)
    # Group by landlord for summary
    landlord_ids = set(b.landlord_id for b in bills_with_balance)
    landlord_totals = {}
    for b in bills_with_balance:
        landlord_totals[b.landlord_id] = landlord_totals.get(b.landlord_id, Decimal('0')) + (b.amount - b.amount_paid)
    return render(request, 'billing/arrears_list.html', {
        'bills': bills_with_balance,
        'total_arrears': total_arrears,
        'landlord_totals': landlord_totals,
    })


# --- Expenses ---

class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = ExpenseType
        fields = ('name', 'pay_frequency', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pay_frequency': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('expense_type', 'amount', 'due_date', 'vendor', 'reference', 'notes')
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpenseListView(AdminDashboardRequiredMixin, LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'billing/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 25

    def get_queryset(self):
        qs = Expense.objects.select_related('expense_type', 'recorded_by').order_by('-due_date', '-created_at')
        status = self.request.GET.get('status')
        if status == 'paid':
            qs = qs.filter(paid_at__isnull=False)
        elif status == 'unpaid':
            qs = qs.filter(paid_at__isnull=True)
        return qs


class ExpenseCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'billing/expense_form.html'
    success_url = reverse_lazy('billing:expense_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        messages.success(self.request, 'Expense recorded.')
        return super().form_valid(form)


class ExpenseUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'billing/expense_form.html'
    context_object_name = 'expense'
    success_url = reverse_lazy('billing:expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Expense updated.')
        return super().form_valid(form)


@admin_dashboard_required
@require_http_methods(['POST'])
def expense_mark_paid(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.paid_at = timezone.now()
    expense.save()
    messages.success(request, f'Marked "{expense}" as paid.')
    return redirect('billing:expense_list')


# --- Labourer payroll (pay every Saturday) ---

class LabourerPaymentForm(forms.ModelForm):
    class Meta:
        model = LabourerPayment
        fields = ('labourer', 'week_ending_date', 'amount', 'reference', 'notes')
        widgets = {
            'labourer': forms.Select(attrs={'class': 'form-select'}),
            'week_ending_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


@admin_dashboard_required
def labourer_payment_list(request):
    """List labourer payments; admins can add new payment."""
    from collection_records.models import CasualLabourer
    payments = LabourerPayment.objects.select_related('labourer', 'recorded_by').order_by('-week_ending_date', 'labourer')
    week_ending = request.GET.get('week')
    if week_ending:
        payments = payments.filter(week_ending_date=week_ending)
    return render(request, 'billing/labourer_payment_list.html', {
        'payments': payments,
        'labourers': CasualLabourer.objects.filter(is_active=True),
    })


class LabourerPaymentCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = LabourerPayment
    form_class = LabourerPaymentForm
    template_name = 'billing/labourer_payment_form.html'
    success_url = reverse_lazy('billing:labourer_payment_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        form.instance.paid_at = timezone.now()  # pay on record
        messages.success(self.request, 'Payment recorded.')
        return super().form_valid(form)


@admin_dashboard_required
def expense_type_list(request):
    """List expense types (e.g. Payroll weekly, Utilities monthly)."""
    types_list = ExpenseType.objects.filter(is_active=True).order_by('name')
    return render(request, 'billing/expense_type_list.html', {'expense_types': types_list})
