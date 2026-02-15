"""Forms for Landlord, Property, Tenant."""
from django import forms
from django.forms import inlineformset_factory
from core.models import Route
from .models import Landlord, Property, PropertyCollectionDay, Tenant


class LandlordForm(forms.ModelForm):
    class Meta:
        model = Landlord
        fields = ('full_name', 'phone', 'email', 'id_number', 'address', 'latitude', 'longitude', 'is_active')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'address': forms.HiddenInput(attrs={'id': 'id_landlord_address'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_landlord_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_landlord_longitude'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = True
        self.fields['email'].required = False
        self.fields['id_number'].required = False


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ('name', 'plot_number', 'physical_address', 'route', 'latitude', 'longitude', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Plot 45, House A'}),
            'plot_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'physical_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Optional'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Optional'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


DAY_NAMES = [(i, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]) for i in range(7)]


class PropertyCollectionDayForm(forms.ModelForm):
    day_of_week = forms.TypedChoiceField(choices=DAY_NAMES, coerce=int, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = PropertyCollectionDay
        fields = ('day_of_week',)


PropertyCollectionDayFormSet = inlineformset_factory(
    Property,
    PropertyCollectionDay,
    form=PropertyCollectionDayForm,
    extra=2,
    max_num=7,
)


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ('full_name', 'phone', 'house_no', 'email', 'monthly_rate', 'is_active')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'house_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House/unit number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'monthly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Leave blank for standard fee'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['house_no'].required = False
        self.fields['monthly_rate'].required = False
