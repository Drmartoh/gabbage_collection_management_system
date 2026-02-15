"""Forms for Ward, Zone, Route, Cart."""
from django import forms
from .models import Ward, Zone, Route, Cart


class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ('name', 'county', 'code', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Karai Ward'}),
            'county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kiambu County'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional code'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ('ward', 'name', 'code', 'description', 'is_active')
        widgets = {
            'ward': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ('zone', 'name', 'code', 'description', 'day_of_week', 'is_active')
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
            'day_of_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 6, 'placeholder': '0=Mon, 6=Sun'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ('code', 'route', 'status', 'notes')
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CART-001'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
        }
