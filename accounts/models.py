"""
Accounts app: User, Role, AuditLog.
Role-based access: Super Admin, Operations Admin, Supervisor, Collector, Landlord, County Officer.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """User role for RBAC."""
    class RoleName(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        OPERATIONS_ADMIN = 'operations_admin', 'Operations Admin'
        SUPERVISOR = 'supervisor', 'Supervisor'
        COLLECTOR = 'collector', 'Collector'
        CASUAL_LABOURER = 'casual_labourer', 'Casual Labourer'
        LANDLORD = 'landlord', 'Landlord'
        COUNTY_OFFICER = 'county_officer', 'County Officer (Read-Only)'

    name = models.CharField(max_length=32, choices=RoleName.choices, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_read_only = models.BooleanField(default=False)  # County Officer

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Custom user with role and phone."""
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_updated_at = models.DateTimeField(auto_now=True)
    # In-app training: first-login welcome and per-page tips
    first_login_tour_done = models.BooleanField(default=False)
    walkthrough_page_tips_seen = models.JSONField(default=list, blank=True)  # list of slugs e.g. ["landlords", "billing"]

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        if self.get_full_name().strip():
            return self.get_full_name()
        return self.username

    @property
    def is_super_admin(self):
        return self.role and self.role.name == Role.RoleName.SUPER_ADMIN

    @property
    def is_operations_admin(self):
        return self.role and self.role.name == Role.RoleName.OPERATIONS_ADMIN

    @property
    def is_supervisor(self):
        return self.role and self.role.name == Role.RoleName.SUPERVISOR

    @property
    def is_collector(self):
        return self.role and self.role.name == Role.RoleName.COLLECTOR

    @property
    def is_landlord(self):
        return self.role and self.role.name == Role.RoleName.LANDLORD

    @property
    def is_county_officer(self):
        return self.role and self.role.name == Role.RoleName.COUNTY_OFFICER

    @property
    def is_read_only(self):
        return self.role and self.role.is_read_only

    def can_edit(self):
        return not self.is_read_only


class AuditLog(models.Model):
    """Audit trail for important actions."""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('export', 'Export'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"
