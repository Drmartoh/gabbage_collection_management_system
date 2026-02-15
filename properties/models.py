"""
Properties app: Landlord, Property, Tenant.
Landlord links to User; properties have route; tenants drive billing (KES 100/month each).
"""
from django.db import models
from django.conf import settings
from core.models import Route


class Landlord(models.Model):
    """Landlord - can link to User (accounts.landlord role)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='landlord_profile'
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True, help_text='Start typing for address suggestions (exact location on map).')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def tenant_count(self):
        from django.db.models import Count
        return self.properties.aggregate(total=Count('tenants')).get('total') or 0

    def billing_amount(self, standard_rate):
        """Total monthly billing: sum of each active tenant's monthly_rate or standard_rate."""
        from decimal import Decimal
        std = Decimal(str(standard_rate))
        total = Decimal('0')
        for prop in self.properties.prefetch_related('tenants').all():
            for t in prop.tenants.filter(is_active=True):
                total += (t.monthly_rate if t.monthly_rate is not None else std)
        return total


class Property(models.Model):
    """Property (plot/building) belonging to a landlord, on a collection route."""
    landlord = models.ForeignKey(
        Landlord,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties'
    )
    name = models.CharField(max_length=200, help_text='e.g. Plot 45, House A')
    plot_number = models.CharField(max_length=50, blank=True)
    physical_address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.name} ({self.landlord.full_name})"

    def tenant_count(self):
        return self.tenants.filter(is_active=True).count()

    def collection_days_display(self):
        """e.g. 'Tue, Sat' from PropertyCollectionDay (default Tue=2, Sat=6 if none)."""
        days = list(
            self.collection_days.order_by('day_of_week').values_list('day_of_week', flat=True)
        )
        if not days:
            days = [2, 6]  # Tuesday, Saturday default
        names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return ', '.join(names[d] for d in days if 0 <= d <= 6)


class PropertyCollectionDay(models.Model):
    """Preferred collection day(s) for a property (default Tue & Sat; can vary per landlord)."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='collection_days'
    )
    day_of_week = models.PositiveSmallIntegerField(
        help_text='0=Monday, 6=Sunday. Tuesday=2, Saturday=6.'
    )

    class Meta:
        ordering = ['property', 'day_of_week']
        unique_together = [['property', 'day_of_week']]

    def __str__(self):
        names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return f"{self.property.name} – {names[self.day_of_week]}"


class Tenant(models.Model):
    """Tenant in a property - one unit of billing; optional per-tenant monthly rate."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='tenants'
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    house_no = models.CharField(max_length=50, blank=True, help_text='House/unit number')
    email = models.EmailField(blank=True)
    monthly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Leave blank to use the standard fee. Set to override for this tenant (KES/month).'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} @ {self.property.name}"
