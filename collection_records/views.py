"""Collection records: route assignments, collection logging, collector dashboard;
casual labourers, zone rotation, garbage collection log."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import role_required, admin_dashboard_required
from accounts.mixins import AdminDashboardRequiredMixin
from accounts.constants import COLLECTOR, SUPERVISOR, CASUAL_LABOURER
from .models import (
    RouteAssignment, CollectionRecord,
    CasualLabourer, LabourerZoneRotation, GarbageCollectionLog,
)
from .forms import (
    RouteAssignmentForm,
    CasualLabourerForm,
    LabourerZoneRotationForm,
    GarbageCollectionLogForm,
)


class AssignmentListView(LoginRequiredMixin, ListView):
    model = RouteAssignment
    template_name = 'collections/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        return RouteAssignment.objects.select_related(
            'route', 'collector', 'cart'
        ).order_by('-date')


class AssignmentCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = RouteAssignment
    form_class = RouteAssignmentForm
    template_name = 'collections/assignment_form.html'
    success_url = reverse_lazy('collections:assignment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Assignment created.')
        return super().form_valid(form)


class AssignmentUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = RouteAssignment
    form_class = RouteAssignmentForm
    template_name = 'collections/assignment_form.html'
    context_object_name = 'assignment'
    success_url = reverse_lazy('collections:assignment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Assignment updated.')
        return super().form_valid(form)


class AssignmentDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = RouteAssignment
    template_name = 'collections/assignment_confirm_delete.html'
    context_object_name = 'assignment'
    success_url = reverse_lazy('collections:assignment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Assignment deleted.')
        return super().form_valid(form)


@role_required(COLLECTOR)
def collector_dashboard(request):
    """Collector's today assignment and collection log."""
    today = timezone.now().date()
    assignment = RouteAssignment.objects.filter(
        collector=request.user,
        date=today
    ).select_related('route', 'cart').first()
    records = []
    if assignment:
        records = assignment.collection_records.select_related('property').all()
    return render(request, 'collections/collector_dashboard.html', {
        'assignment': assignment,
        'records': records,
    })


@role_required(COLLECTOR)
def log_collection(request, record_id):
    """Collector marks a property as collected (with optional GPS)."""
    record = get_object_or_404(CollectionRecord, pk=record_id, assignment__collector=request.user)
    if request.method == 'POST':
        record.status = 'collected'
        record.collected_at = timezone.now()
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        if lat and lon:
            from decimal import Decimal
            try:
                record.latitude = Decimal(lat)
                record.longitude = Decimal(lon)
            except Exception:
                pass
        record.notes = request.POST.get('notes', '')
        record.save()
        messages.success(request, 'Collection recorded.')
        return redirect('collections:collector_dashboard')
    return render(request, 'collections/log_collection.html', {'record': record})


@role_required(SUPERVISOR)
def verify_collection(request, record_id):
    """Supervisor verifies a collection record."""
    record = get_object_or_404(CollectionRecord, pk=record_id)
    if request.method == 'POST' and request.user.is_supervisor:
        record.status = 'verified'
        record.verified_by = request.user
        record.verified_at = timezone.now()
        record.verification_notes = request.POST.get('verification_notes', '')
        record.save()
        messages.success(request, 'Collection verified.')
        return redirect('collections:assignment_list')
    return render(request, 'collections/verify_collection.html', {'record': record})


# --- Casual labourers (supervisor assigns; rotate by zone) ---

class LabourerListView(AdminDashboardRequiredMixin, LoginRequiredMixin, ListView):
    model = CasualLabourer
    template_name = 'collections/labourer_list.html'
    context_object_name = 'labourers'
    paginate_by = 25


class LabourerCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = CasualLabourer
    form_class = CasualLabourerForm
    template_name = 'collections/labourer_form.html'
    success_url = reverse_lazy('collections:labourer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Casual labourer added.')
        return super().form_valid(form)


class LabourerUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = CasualLabourer
    form_class = CasualLabourerForm
    template_name = 'collections/labourer_form.html'
    context_object_name = 'labourer'
    success_url = reverse_lazy('collections:labourer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Labourer updated.')
        return super().form_valid(form)


class LabourerDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = CasualLabourer
    template_name = 'collections/labourer_confirm_delete.html'
    context_object_name = 'labourer'
    success_url = reverse_lazy('collections:labourer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Labourer removed.')
        return super().form_valid(form)


# --- Labourer zone rotation (supervisor assigns labourer to zone) ---

class LabourerRotationListView(AdminDashboardRequiredMixin, LoginRequiredMixin, ListView):
    model = LabourerZoneRotation
    template_name = 'collections/labourer_rotation_list.html'
    context_object_name = 'rotations'
    paginate_by = 25

    def get_queryset(self):
        return LabourerZoneRotation.objects.select_related(
            'labourer', 'zone', 'assigned_by'
        ).order_by('-valid_from', 'zone')


class LabourerRotationCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = LabourerZoneRotation
    form_class = LabourerZoneRotationForm
    template_name = 'collections/labourer_rotation_form.html'
    success_url = reverse_lazy('collections:labourer_rotation_list')

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        messages.success(self.request, 'Rotation assigned.')
        return super().form_valid(form)


class LabourerRotationUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = LabourerZoneRotation
    form_class = LabourerZoneRotationForm
    template_name = 'collections/labourer_rotation_form.html'
    context_object_name = 'rotation'
    success_url = reverse_lazy('collections:labourer_rotation_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rotation updated.')
        return super().form_valid(form)


# --- Garbage collection log (form filled when labourer collects: where, when, who, incident) ---

class GarbageCollectionLogListView(LoginRequiredMixin, ListView):
    model = GarbageCollectionLog
    template_name = 'collections/garbage_collection_log_list.html'
    context_object_name = 'logs'
    paginate_by = 25

    def get_queryset(self):
        qs = GarbageCollectionLog.objects.select_related(
            'labourer', 'property', 'zone', 'landlord', 'recorded_by'
        ).order_by('-collection_date', '-collection_time', '-created_at')
        if getattr(self.request.user, 'casual_labourer_profile', None):
            qs = qs.filter(labourer=self.request.user.casual_labourer_profile)
        return qs


class GarbageCollectionLogCreateView(LoginRequiredMixin, CreateView):
    model = GarbageCollectionLog
    form_class = GarbageCollectionLogForm
    template_name = 'collections/garbage_collection_log_form.html'
    success_url = reverse_lazy('collections:garbage_log_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        if not form.instance.landlord_id and form.instance.property_id:
            form.instance.landlord = form.instance.property.landlord
        if not form.instance.zone_id and form.instance.property_id and form.instance.property.route_id:
            form.instance.zone = form.instance.property.route.zone
        messages.success(self.request, 'Collection logged.')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile = getattr(self.request.user, 'casual_labourer_profile', None)
        if profile:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['labourer'] = profile
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        profile = getattr(self.request.user, 'casual_labourer_profile', None)
        if profile:
            form.fields['labourer'].queryset = CasualLabourer.objects.filter(pk=profile.pk)
            form.fields['labourer'].initial = profile
        return form
