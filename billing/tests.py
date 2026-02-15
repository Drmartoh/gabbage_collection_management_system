"""Tests for billing: overpayment rejection, balance after payment."""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import Role
from properties.models import Landlord
from billing.models import BillingCycle, LandlordBill, PaymentRecord

User = get_user_model()


class BillingPaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(name='operations_admin', description='Ops')
        self.user = User.objects.create_user(username='ops', password='testpass123', role=self.role)
        self.landlord = Landlord.objects.create(full_name='Test Landlord', phone='+254700000000', email='l@test.com')
        self.cycle = BillingCycle.objects.create(year=2025, month=2)
        self.bill = LandlordBill.objects.create(
            cycle=self.cycle,
            landlord=self.landlord,
            tenant_count=5,
            amount=Decimal('500'),
            amount_paid=Decimal('0'),
        )
        # Existing payments that sum to 200 (signal keeps amount_paid in sync)
        PaymentRecord.objects.create(bill=self.bill, amount=Decimal('200'), method='mpesa', recorded_by=self.user)
        self.bill.refresh_from_db()

    def test_overpayment_rejected(self):
        self.client.force_login(self.user)
        url = reverse('billing:record_payment', kwargs={'bill_id': self.bill.pk})
        # Balance is 500 - 200 = 300. Paying 400 should be rejected.
        resp = self.client.post(url, {'amount': '400', 'method': 'mpesa', 'reference': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'exceeds balance', status_code=200)
        self.assertEqual(PaymentRecord.objects.filter(bill=self.bill).count(), 1)  # only pre-existing

    def test_valid_payment_updates_balance(self):
        self.client.force_login(self.user)
        url = reverse('billing:record_payment', kwargs={'bill_id': self.bill.pk})
        resp = self.client.post(url, {'amount': '100', 'method': 'mpesa', 'reference': 'REF1'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(PaymentRecord.objects.filter(bill=self.bill).count(), 2)  # existing 200 + new 100
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.amount_paid, Decimal('300'))
        self.assertEqual(self.bill.balance, Decimal('200'))
