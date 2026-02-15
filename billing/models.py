"""
Billing app: landlord-based monthly billing at KES 100 per tenant;
expenses (weekly vs end-of-month), payroll for casual labourers.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from properties.models import Landlord


class BillingCycle(models.Model):
    """Monthly billing period."""
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = [['year', 'month']]

    def __str__(self):
        return f"{self.year}-{self.month:02d}"


class LandlordBill(models.Model):
    """Per-landlord bill for a cycle (amount = tenant_count * 100)."""
    cycle = models.ForeignKey(BillingCycle, on_delete=models.CASCADE, related_name='bills')
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='bills')
    tenant_count = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-cycle', 'landlord']
        unique_together = [['cycle', 'landlord']]

    def __str__(self):
        return f"{self.landlord} - {self.cycle} (KES {self.amount})"

    @property
    def balance(self):
        return self.amount - self.amount_paid


class PaymentRecord(models.Model):
    """Payment against a landlord bill."""
    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    bill = models.ForeignKey(
        LandlordBill,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='mpesa')
    reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_payments'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"KES {self.amount} - {self.bill.landlord} ({self.paid_at.date()})"


def _update_bill_paid(sender, instance, **kwargs):
    from django.db.models import Sum
    if instance.bill_id:
        total = PaymentRecord.objects.filter(bill_id=instance.bill_id).aggregate(
            t=Sum('amount')
        ).get('t') or Decimal('0')
        LandlordBill.objects.filter(pk=instance.bill_id).update(amount_paid=total)


models.signals.post_save.connect(_update_bill_paid, sender=PaymentRecord)
models.signals.post_delete.connect(_update_bill_paid, sender=PaymentRecord)


# --- Expenses & Payroll ---

class ExpenseType(models.Model):
    """Type of expense (Payroll, Fuel, Maintenance, etc.) with pay frequency."""
    PAY_FREQUENCY = [
        ('weekly', 'Weekly (e.g. every Saturday)'),
        ('monthly', 'End of month'),
    ]
    name = models.CharField(max_length=100)
    pay_frequency = models.CharField(max_length=20, choices=PAY_FREQUENCY, default='monthly')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Outstanding or paid expense; some paid weekly (e.g. Saturday), others end of month."""
    expense_type = models.ForeignKey(
        ExpenseType,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    vendor = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.expense_type.name} – KES {self.amount}"

    @property
    def is_paid(self):
        return self.paid_at is not None


class LabourerPayment(models.Model):
    """Pay casual labourers every Saturday (week-ending)."""
    labourer = models.ForeignKey(
        'collection_records.CasualLabourer',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    week_ending_date = models.DateField(help_text='Saturday date for the week')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_labourer_payments'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_ending_date', 'labourer']
        unique_together = [['labourer', 'week_ending_date']]

    def __str__(self):
        return f"{self.labourer} – {self.week_ending_date} KES {self.amount}"
