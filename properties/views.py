"""Properties: landlords, properties, tenants."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from accounts.decorators import role_required
from accounts.mixins import AdminDashboardRequiredMixin
from accounts.constants import LANDLORD
from .models import Landlord, Property, Tenant
from .forms import LandlordForm, PropertyForm, PropertyCollectionDayFormSet, TenantForm


class TenantListView(AdminDashboardRequiredMixin, LoginRequiredMixin, ListView):
    """List all tenants across properties (name, phone, house no, email, property, landlord)."""
    model = Tenant
    template_name = 'properties/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 25

    def get_queryset(self):
        return Tenant.objects.select_related('property', 'property__landlord').order_by('property__landlord__full_name', 'property__name', 'full_name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Tenants'},
        ]
        return ctx


class LandlordListView(LoginRequiredMixin, ListView):
    model = Landlord
    template_name = 'properties/landlord_list.html'
    context_object_name = 'landlords'

    def get_queryset(self):
        return Landlord.objects.prefetch_related('properties').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.urls import reverse
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Landlords'},
        ]
        return ctx


class LandlordCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Landlord
    form_class = LandlordForm
    template_name = 'properties/landlord_form.html'
    success_url = reverse_lazy('properties:landlord_list')

    def form_valid(self, form):
        messages.success(self.request, 'Landlord created.')
        return super().form_valid(form)


class LandlordUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Landlord
    form_class = LandlordForm
    template_name = 'properties/landlord_form.html'
    context_object_name = 'landlord'
    success_url = reverse_lazy('properties:landlord_list')

    def form_valid(self, form):
        messages.success(self.request, 'Landlord updated.')
        return super().form_valid(form)


class LandlordDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Landlord
    template_name = 'properties/landlord_confirm_delete.html'
    context_object_name = 'landlord'
    success_url = reverse_lazy('properties:landlord_list')

    def form_valid(self, form):
        messages.success(self.request, 'Landlord deleted.')
        return super().form_valid(form)


class LandlordDetailView(AdminDashboardRequiredMixin, LoginRequiredMixin, DetailView):
    model = Landlord
    template_name = 'properties/landlord_detail.html'
    context_object_name = 'landlord'

    def get_queryset(self):
        return Landlord.objects.prefetch_related('properties__route', 'properties__tenants').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.urls import reverse
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Landlords', 'url': reverse('properties:landlord_list')},
            {'label': self.object.full_name},
        ]
        return ctx


class PropertyCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def get_initial(self):
        initial = super().get_initial()
        landlord_id = self.kwargs.get('landlord_id')
        if landlord_id:
            initial['landlord'] = get_object_or_404(Landlord, pk=landlord_id)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landlord'] = get_object_or_404(Landlord, pk=self.kwargs['landlord_id'])
        if self.request.POST:
            ctx['collection_days_formset'] = PropertyCollectionDayFormSet(self.request.POST)
        else:
            ctx['collection_days_formset'] = PropertyCollectionDayFormSet()
        return ctx

    def form_valid(self, form):
        form.instance.landlord_id = self.kwargs['landlord_id']
        self.object = form.save()
        collection_days_formset = PropertyCollectionDayFormSet(self.request.POST, instance=self.object)
        if collection_days_formset.is_valid():
            collection_days_formset.save()
        messages.success(self.request, 'Property created.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('properties:landlord_detail', kwargs={'pk': self.kwargs['landlord_id']})


class PropertyUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    context_object_name = 'property_obj'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landlord'] = self.object.landlord
        if self.request.POST:
            ctx['collection_days_formset'] = PropertyCollectionDayFormSet(self.request.POST, instance=self.object)
        else:
            ctx['collection_days_formset'] = PropertyCollectionDayFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        collection_days_formset = context['collection_days_formset']
        if collection_days_formset.is_valid():
            form.save()
            collection_days_formset.save()
            messages.success(self.request, 'Property updated.')
            return redirect(self.get_success_url())
        context['form'] = form
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('properties:landlord_detail', kwargs={'pk': self.object.landlord_id})


class PropertyDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    context_object_name = 'property_obj'

    def form_valid(self, form):
        self._landlord_id = self.object.landlord_id
        messages.success(self.request, 'Property deleted.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:landlord_detail', kwargs={'pk': self._landlord_id})


class PropertyDetailView(AdminDashboardRequiredMixin, LoginRequiredMixin, DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property_obj'

    def get_queryset(self):
        return Property.objects.select_related('landlord', 'route').prefetch_related('tenants').all()


class TenantCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'properties/tenant_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['property_obj'] = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return ctx

    def form_valid(self, form):
        form.instance.property_id = self.kwargs['property_id']
        messages.success(self.request, 'Tenant added.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:property_detail', kwargs={'pk': self.kwargs['property_id']})


class TenantUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'properties/tenant_form.html'
    context_object_name = 'tenant'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['property_obj'] = self.object.property
        return ctx

    def get_success_url(self):
        return reverse('properties:property_detail', kwargs={'pk': self.object.property_id})


class TenantDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Tenant
    template_name = 'properties/tenant_confirm_delete.html'
    context_object_name = 'tenant'

    def form_valid(self, form):
        self._property_id = self.object.property_id
        messages.success(self.request, 'Tenant removed.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:property_detail', kwargs={'pk': self._property_id})


@role_required(LANDLORD)
def landlord_dashboard(request):
    """Landlord's own properties and tenants."""
    try:
        profile = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.warning(request, 'No landlord profile linked to your account.')
        return redirect('accounts:dashboard_redirect')
    properties = profile.properties.prefetch_related('tenants').filter(is_active=True)
    return render(request, 'properties/landlord_dashboard.html', {'profile': profile, 'properties': properties})
