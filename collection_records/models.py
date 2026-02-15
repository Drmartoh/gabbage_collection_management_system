"""
Collection records app: RouteAssignment, CollectionRecord, CasualLabourer,
LabourerZoneRotation, GarbageCollectionLog.
Daily collection logging, supervisor verification, geolocation capture.
Casual labourers rotate by zone; they fill a form per collection (where, when, who, incident).
"""
from django.db import models
from django.conf import settings
from core.models import Route, Cart, Zone
from properties.models import Property, Landlord


class RouteAssignment(models.Model):
    """Assign collector(s) and cart(s) to a route (e.g. per day)."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='assignments')
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__name': 'collector'},
        related_name='route_assignments'
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='route_assignments'
    )
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'route']
        unique_together = [['route', 'date']]

    def __str__(self):
        return f"{self.route.name} on {self.date} ({self.collector.get_display_name()})"


class CollectionRecord(models.Model):
    """Daily collection log per property - with geolocation and supervisor verification."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('collected', 'Collected'),
        ('verified', 'Verified'),
        ('skipped', 'Skipped'),
        ('issue', 'Issue'),
    ]
    assignment = models.ForeignKey(
        RouteAssignment,
        on_delete=models.CASCADE,
        related_name='collection_records'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='collection_records'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    collected_at = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__name': 'supervisor'},
        related_name='verified_collections'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['assignment', 'property']]

    def __str__(self):
        return f"{self.property} - {self.get_status_display()} ({self.assignment.date})"


class CasualLabourer(models.Model):
    """Casual labourer (rotating; paid weekly on Saturday). Can optionally link to User to log collections."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='casual_labourer_profile'
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class LabourerZoneRotation(models.Model):
    """Supervisor assigns a casual labourer to a zone (valid for a period)."""
    labourer = models.ForeignKey(
        CasualLabourer,
        on_delete=models.CASCADE,
        related_name='zone_rotations'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='labourer_rotations'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='labourer_assignments_made'
    )
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-valid_from', 'zone']

    def __str__(self):
        return f"{self.labourer} → {self.zone} ({self.valid_from})"


class GarbageCollectionLog(models.Model):
    """Form filled when casual labourer collects garbage: where, when, who (landlord), dispute/incident. Populates system."""
    labourer = models.ForeignKey(
        CasualLabourer,
        on_delete=models.CASCADE,
        related_name='collection_logs'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='garbage_collection_logs'
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='garbage_collection_logs',
        null=True,
        blank=True
    )
    collection_date = models.DateField()
    collection_time = models.TimeField(null=True, blank=True)
    landlord = models.ForeignKey(
        Landlord,
        on_delete=models.CASCADE,
        related_name='garbage_collection_logs',
        null=True,
        blank=True
    )
    incident_or_dispute = models.TextField(blank=True, help_text='Any dispute or incident during collection')
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_garbage_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collection_date', '-collection_time', '-created_at']

    def __str__(self):
        return f"{self.property.name} by {self.labourer} on {self.collection_date}"
