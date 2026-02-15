"""Forms for RouteAssignment, CasualLabourer, LabourerZoneRotation, GarbageCollectionLog."""
from django import forms
from django.contrib.auth import get_user_model
from .models import (
    RouteAssignment,
    CasualLabourer,
    LabourerZoneRotation,
    GarbageCollectionLog,
)

User = get_user_model()


class RouteAssignmentForm(forms.ModelForm):
    class Meta:
        model = RouteAssignment
        fields = ('route', 'collector', 'cart', 'date', 'notes', 'is_completed')
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'collector': forms.Select(attrs={'class': 'form-select'}),
            'cart': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        collectors = User.objects.filter(role__name='collector').order_by('username')
        self.fields['collector'].queryset = collectors


class CasualLabourerForm(forms.ModelForm):
    class Meta:
        model = CasualLabourer
        fields = ('full_name', 'phone', 'id_number', 'user', 'is_active')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labourers = User.objects.filter(role__name='casual_labourer').order_by('username')
        self.fields['user'].queryset = labourers
        self.fields['user'].required = False


class LabourerZoneRotationForm(forms.ModelForm):
    class Meta:
        model = LabourerZoneRotation
        fields = ('labourer', 'zone', 'valid_from', 'valid_to', 'notes')
        widgets = {
            'labourer': forms.Select(attrs={'class': 'form-select'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class GarbageCollectionLogForm(forms.ModelForm):
    class Meta:
        model = GarbageCollectionLog
        fields = (
            'labourer', 'property', 'zone', 'collection_date', 'collection_time',
            'landlord', 'incident_or_dispute', 'notes',
        )
        widgets = {
            'labourer': forms.Select(attrs={'class': 'form-select'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'collection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'collection_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'landlord': forms.Select(attrs={'class': 'form-select'}),
            'incident_or_dispute': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any dispute or incident during collection'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone'].required = False
        self.fields['landlord'].required = False
        self.fields['collection_time'].required = False
        from properties.models import Property, Landlord
        from core.models import Zone
        self.fields['property'].queryset = Property.objects.filter(is_active=True).select_related('landlord').order_by('name')
        self.fields['landlord'].queryset = Landlord.objects.filter(is_active=True).order_by('full_name')
        self.fields['zone'].queryset = Zone.objects.filter(is_active=True).order_by('name')
        self.fields['labourer'].queryset = CasualLabourer.objects.filter(is_active=True).order_by('full_name')
