"""Generate landlord bills for a given month (standard + per-tenant rate)."""
from django.core.management.base import BaseCommand
from properties.models import Landlord
from billing.models import BillingCycle, LandlordBill
from billing.views import get_standard_rate


class Command(BaseCommand):
    help = 'Generate monthly bills for all landlords (year, month).'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        cycle, _ = BillingCycle.objects.get_or_create(year=year, month=month, defaults={'is_closed': False})
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
        self.stdout.write(self.style.SUCCESS(f'Created/updated {count} bills for {year}-{month}.'))
