"""
Core app: Ward, Zone, Route, Cart, SystemSetting.
Karai Ward, Kiambu County - single ward with multiple zones and routes.
"""
from django.db import models
from django.conf import settings


class SystemSetting(models.Model):
    """Key-value store for GCMS settings editable from the Settings page (e.g. in-app walkthrough)."""
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return f"{self.key}={self.value}"

    @classmethod
    def get_value(cls, key, default=''):
        try:
            obj = cls.objects.get(key=key)
            return obj.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value, description=''):
        obj, _ = cls.objects.get_or_create(key=key, defaults={'value': '', 'description': description})
        obj.value = str(value)
        obj.save(update_fields=['value', 'updated_at'])


class Ward(models.Model):
    """Ward within a county (e.g. Karai Ward, Kiambu County)."""
    name = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.county}"


class Zone(models.Model):
    """Zone within a ward (collection area)."""
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [['ward', 'name']]

    def __str__(self):
        return f"{self.name} ({self.ward.name})"


class Route(models.Model):
    """Collection route within a zone."""
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    day_of_week = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='0=Monday, 6=Sunday'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['zone', 'name']
        unique_together = [['zone', 'name']]

    def __str__(self):
        return f"{self.name} ({self.zone.name})"


class Cart(models.Model):
    """Waste collection cart (physical asset)."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]
    code = models.CharField(max_length=50, unique=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code
