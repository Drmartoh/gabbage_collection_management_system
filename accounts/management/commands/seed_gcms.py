"""Seed GCMS with roles, Karai Ward, sample data."""
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role
from core.models import Ward, Zone, Route, Cart
from properties.models import Landlord, Property, Tenant
from billing.models import BillingCycle, LandlordBill
from django.conf import settings


class Command(BaseCommand):
    help = 'Seed roles, Karai Ward, zones, routes, sample landlord and billing.'

    def handle(self, *args, **options):
        # Ensure database tables exist (run migrate first)
        self.stdout.write('Running migrations...')
        call_command('migrate', '--noinput', verbosity=1)
        self.stdout.write('Migrations done.')

        # Roles
        for name, label, read_only in [
            ('super_admin', 'Super Admin', False),
            ('operations_admin', 'Operations Admin', False),
            ('supervisor', 'Supervisor', False),
            ('collector', 'Collector', False),
            ('landlord', 'Landlord', False),
            ('county_officer', 'County Officer (Read-Only)', True),
        ]:
            Role.objects.get_or_create(name=name, defaults={'description': label, 'is_read_only': read_only})
        self.stdout.write('Roles created.')

        # Ward
        ward, _ = Ward.objects.get_or_create(
            code='KARAI',
            defaults={'name': 'Karai Ward', 'county': 'Kiambu County', 'is_active': True}
        )
        # Zone
        zone, _ = Zone.objects.get_or_create(
            ward=ward,
            name='Karai Central',
            defaults={'code': 'KC', 'is_active': True}
        )
        # Route
        route, _ = Route.objects.get_or_create(
            zone=zone,
            name='Route A',
            defaults={'code': 'R-A', 'day_of_week': 0, 'is_active': True}
        )
        # Cart
        cart, _ = Cart.objects.get_or_create(
            code='CART-001',
            defaults={'route': route, 'status': 'active'}
        )
        self.stdout.write('Ward, zone, route, cart created.')

        # Sample landlord (no user link by default)
        landlord, _ = Landlord.objects.get_or_create(
            phone='+254700000001',
            defaults={
                'full_name': 'Sample Landlord',
                'email': 'landlord@example.com',
                'is_active': True,
            }
        )
        prop, _ = Property.objects.get_or_create(
            landlord=landlord,
            name='Plot 1 House A',
            defaults={'route': route, 'plot_number': 'P1', 'is_active': True}
        )
        Tenant.objects.get_or_create(
            property=prop,
            full_name='Tenant One',
            defaults={'phone': '+254700000002', 'is_active': True}
        )
        self.stdout.write('Sample landlord, property, tenant created.')

        # Billing cycle and bill
        now = timezone.now()
        cycle, _ = BillingCycle.objects.get_or_create(
            year=now.year,
            month=now.month,
            defaults={'is_closed': False}
        )
        rate = Decimal(getattr(settings, 'GCMS_RATE_PER_TENANT_MONTHLY', 100))
        for ll in Landlord.objects.filter(is_active=True):
            count = ll.tenant_count()
            if count > 0:
                amount = Decimal(count) * rate
                bill, created = LandlordBill.objects.get_or_create(
                    cycle=cycle,
                    landlord=ll,
                    defaults={'tenant_count': count, 'amount': amount}
                )
                if not created:
                    bill.tenant_count = count
                    bill.amount = amount
                    bill.save()
        self.stdout.write('Billing cycle and bills created.')
        self.stdout.write(self.style.SUCCESS('Seed completed. Create superuser with: python manage.py createsuperuser'))
