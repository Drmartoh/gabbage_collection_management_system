"""Incidents: report with photo upload and GPS."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.forms import inlineformset_factory

from accounts.mixins import AdminDashboardRequiredMixin
from .models import IncidentReport, IncidentPhoto

IncidentPhotoFormSet = inlineformset_factory(
    IncidentReport,
    IncidentPhoto,
    fields=('image', 'caption'),
    extra=2,
    max_num=10,
    widgets={
        'image': forms.FileInput(attrs={'class': 'form-control'}),
        'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
    },
)


class IncidentListView(LoginRequiredMixin, ListView):
    model = IncidentReport
    template_name = 'incidents/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 20

    def get_queryset(self):
        return IncidentReport.objects.select_related('property', 'reported_by').order_by('-reported_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.urls import reverse
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Incidents'},
        ]
        return ctx


class IncidentForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ('title', 'description', 'severity', 'status', 'property', 'latitude', 'longitude')


class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = IncidentReport
    form_class = IncidentForm
    template_name = 'incidents/incident_form.html'
    success_url = reverse_lazy('incidents:incident_list')

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, 'is_read_only', False):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('Read-only access.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['photo_formset'] = IncidentPhotoFormSet(self.request.POST, self.request.FILES)
        else:
            ctx['photo_formset'] = IncidentPhotoFormSet()
        from django.urls import reverse
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Incidents', 'url': reverse('incidents:incident_list')},
            {'label': 'Report incident'},
        ]
        return ctx

    def form_valid(self, form):
        from accounts.utils import log_audit
        form.instance.reported_by = self.request.user
        self.object = form.save()
        photo_formset = IncidentPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if photo_formset.is_valid():
            photo_formset.save()
        log_audit(
            self.request.user,
            'create',
            model_name='IncidentReport',
            object_id=self.object.pk,
            object_repr=self.object.title,
            message=f'Incident reported: {self.object.title}',
            request=self.request,
        )
        messages.success(self.request, 'Incident reported.')
        return redirect(self.get_success_url())


class IncidentUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = IncidentReport
    form_class = IncidentForm
    template_name = 'incidents/incident_form.html'
    context_object_name = 'incident'
    success_url = reverse_lazy('incidents:incident_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['photo_formset'] = IncidentPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            ctx['photo_formset'] = IncidentPhotoFormSet(instance=self.object)
        from django.urls import reverse
        ctx['breadcrumbs'] = [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Incidents', 'url': reverse('incidents:incident_list')},
            {'label': f'Edit: {self.object.title}'},
        ]
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        if photo_formset.is_valid():
            form.save()
            photo_formset.save()
            messages.success(self.request, 'Incident updated.')
            return redirect(self.get_success_url())
        context['form'] = form
        return self.render_to_response(context)


class IncidentDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = IncidentReport
    template_name = 'incidents/incident_confirm_delete.html'
    context_object_name = 'incident'
    success_url = reverse_lazy('incidents:incident_list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident deleted.')
        return super().form_valid(form)


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    return render(request, 'incidents/incident_detail.html', {'incident': incident})
