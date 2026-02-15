"""Core app views: admin dashboard, wards, zones, routes, carts, analytics, walkthrough API."""
import json
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.decorators import admin_dashboard_required
from accounts.mixins import AdminDashboardRequiredMixin
from .models import Ward, Zone, Route, Cart
from .forms import WardForm, ZoneForm, RouteForm, CartForm


@admin_dashboard_required
def ward_map(request):
    """Live map view for Kikuyu Constituency, Karai Ward."""
    from django.urls import reverse
    return render(request, 'core/ward_map.html', {
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Ward map'},
        ],
    })


@admin_dashboard_required
def gcms_settings_page(request):
    """Show GCMS configuration; allow toggling in-app walkthrough."""
    from django.urls import reverse
    from django.conf import settings as django_settings
    from .models import SystemSetting

    if request.method == 'POST':
        if 'walkthrough_enabled' in request.POST:
            val = request.POST.get('walkthrough_enabled', 'false').lower() in ('true', '1', 'yes')
            SystemSetting.set_value('walkthrough_enabled', 'true' if val else 'false', 'Show in-app training on first login and per-page tips')
            messages.success(request, 'In-app training setting updated.')
            return redirect('core:gcms_settings')
        if 'rate_per_tenant' in request.POST:
            try:
                r = int(request.POST.get('rate_per_tenant', 0))
                if r < 0:
                    raise ValueError('Rate must be ≥ 0')
                SystemSetting.set_value('billing_rate_per_tenant', str(r), 'Default monthly fee per tenant (KES)')
                messages.success(request, 'Standard fee (rate per tenant) updated.')
                return redirect('core:gcms_settings')
            except (ValueError, TypeError):
                messages.error(request, 'Enter a valid whole number for the fee.')

    walkthrough_enabled = SystemSetting.get_value('walkthrough_enabled', 'true').lower() in ('true', '1', 'yes')
    rate_from_setting = SystemSetting.get_value('billing_rate_per_tenant', '')
    rate_per_tenant = int(rate_from_setting) if rate_from_setting.isdigit() else getattr(django_settings, 'GCMS_RATE_PER_TENANT_MONTHLY', 100)
    return render(request, 'core/settings.html', {
        'site_name': getattr(django_settings, 'GCMS_SITE_NAME', 'GCMS'),
        'ward': getattr(django_settings, 'GCMS_WARD', ''),
        'county': getattr(django_settings, 'GCMS_COUNTY', ''),
        'rate_per_tenant': rate_per_tenant,
        'here_configured': bool(getattr(django_settings, 'HERE_API_KEY', '')),
        'sms_configured': bool(
            getattr(django_settings, 'GCMS_SMS_API_URL', '') and getattr(django_settings, 'GCMS_SMS_API_KEY', '')
        ),
        'session_hours': getattr(django_settings, 'SESSION_COOKIE_AGE', 28800) // 3600,
        'walkthrough_enabled': walkthrough_enabled,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Settings'},
        ],
    })


@login_required
@require_POST
def walkthrough_mark_welcome_done(request):
    """Mark first-login welcome tour as completed for the current user."""
    request.user.first_login_tour_done = True
    request.user.save(update_fields=['first_login_tour_done'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def walkthrough_mark_page_seen(request):
    """Mark a page tip as seen (add slug to user's walkthrough_page_tips_seen)."""
    slug = request.POST.get('slug', '').strip()
    if not slug and request.content_type == 'application/json' and request.body:
        try:
            slug = (json.loads(request.body).get('slug') or '').strip()
        except (ValueError, TypeError):
            pass
    if not slug:
        return JsonResponse({'ok': False, 'error': 'slug required'}, status=400)
    seen = list(request.user.walkthrough_page_tips_seen or [])
    if slug not in seen:
        seen.append(slug)
        request.user.walkthrough_page_tips_seen = seen
        request.user.save(update_fields=['walkthrough_page_tips_seen'])
    return JsonResponse({'ok': True})


@admin_dashboard_required
def properties_heatmap(request):
    """Live heat map of all registered properties with location; click marker for landlord & property details."""
    from django.urls import reverse
    from properties.models import Property
    properties = list(
        Property.objects.filter(is_active=True)
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .select_related('landlord', 'route', 'route__zone')
        .order_by('name')
    )
    places = []
    for p in properties:
        places.append({
            'id': p.pk,
            'name': p.name or 'Property',
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'landlord_name': p.landlord.full_name,
            'landlord_phone': p.landlord.phone or '',
            'landlord_email': p.landlord.email or '',
            'landlord_address': p.landlord.address or '',
            'address': p.physical_address or '',
            'plot_number': p.plot_number or '',
            'route_name': p.route.name if p.route else '',
            'zone_name': p.route.zone.name if p.route and p.route.zone else '',
            'property_url': reverse('properties:property_detail', kwargs={'pk': p.pk}),
            'tenant_count': p.tenant_count(),
        })
    return render(request, 'core/properties_heatmap.html', {
        'places': places,
        'places_json': json.dumps(places),
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Properties map'},
        ],
    })


@admin_dashboard_required
def route_map(request, pk):
    """Show all properties on a route on a HERE map (live data)."""
    route = get_object_or_404(Route, pk=pk)
    from properties.models import Property
    properties = list(
        route.properties.filter(is_active=True).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    )
    markers = [
        {'lat': float(p.latitude), 'lng': float(p.longitude), 'label': p.name or 'Property'}
        for p in properties
    ]
    markers_json = json.dumps(markers)
    from django.urls import reverse
    return render(request, 'core/route_map.html', {
        'route': route,
        'markers': markers,
        'markers_json': markers_json,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': reverse('core:admin_dashboard')},
            {'label': 'Routes', 'url': reverse('core:route_list')},
            {'label': route.name + ' — Map'},
        ],
    })


@admin_dashboard_required
def admin_dashboard(request):
    """AGCBO admin dashboard."""
    from properties.models import Property, Tenant
    from collection_records.models import RouteAssignment, CollectionRecord
    from billing.models import LandlordBill, BillingCycle
    from incidents.models import IncidentReport

    today = timezone.now().date()
    wards = Ward.objects.filter(is_active=True).count()
    routes = Route.objects.filter(is_active=True).count()
    properties = Property.objects.filter(is_active=True).count()
    tenants = Tenant.objects.filter(property__is_active=True).count()
    today_assignments = RouteAssignment.objects.filter(date=today)
    today_collections = CollectionRecord.objects.filter(assignment__date=today)
    open_incidents = IncidentReport.objects.exclude(status__in=('resolved', 'closed')).count()
    current_cycle = BillingCycle.objects.filter(is_closed=False).order_by('-year', '-month').first()
    total_billed = LandlordBill.objects.filter(cycle=current_cycle).aggregate(
        t=Sum('amount'))['t'] or 0
    total_paid = LandlordBill.objects.filter(cycle=current_cycle).aggregate(
        t=Sum('amount_paid'))['t'] or 0

    context = {
        'wards': wards,
        'routes': routes,
        'properties': properties,
        'tenants': tenants,
        'today_assignments': today_assignments,
        'today_collections': today_collections,
        'open_incidents': open_incidents,
        'current_cycle': current_cycle,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'breadcrumbs': [{'label': 'Dashboard'}],
    }
    return render(request, 'core/admin_dashboard.html', context)


class WardListView(LoginRequiredMixin, ListView):
    model = Ward
    template_name = 'core/ward_list.html'
    context_object_name = 'wards'


class WardCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Ward
    form_class = WardForm
    template_name = 'core/ward_form.html'
    success_url = reverse_lazy('core:ward_list')

    def form_valid(self, form):
        messages.success(self.request, 'Ward created.')
        return super().form_valid(form)


class WardUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Ward
    form_class = WardForm
    template_name = 'core/ward_form.html'
    context_object_name = 'ward'
    success_url = reverse_lazy('core:ward_list')

    def form_valid(self, form):
        messages.success(self.request, 'Ward updated.')
        return super().form_valid(form)


class WardDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Ward
    template_name = 'core/ward_confirm_delete.html'
    context_object_name = 'ward'
    success_url = reverse_lazy('core:ward_list')

    def form_valid(self, form):
        messages.success(self.request, 'Ward deleted.')
        return super().form_valid(form)


class ZoneListView(LoginRequiredMixin, ListView):
    model = Zone
    template_name = 'core/zone_list.html'
    context_object_name = 'zones'

    def get_queryset(self):
        return Zone.objects.select_related('ward').all()


class ZoneCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Zone
    form_class = ZoneForm
    template_name = 'core/zone_form.html'
    success_url = reverse_lazy('core:zone_list')

    def form_valid(self, form):
        messages.success(self.request, 'Zone created.')
        return super().form_valid(form)


class ZoneUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Zone
    form_class = ZoneForm
    template_name = 'core/zone_form.html'
    context_object_name = 'zone'
    success_url = reverse_lazy('core:zone_list')

    def form_valid(self, form):
        messages.success(self.request, 'Zone updated.')
        return super().form_valid(form)


class ZoneDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Zone
    template_name = 'core/zone_confirm_delete.html'
    context_object_name = 'zone'
    success_url = reverse_lazy('core:zone_list')

    def form_valid(self, form):
        messages.success(self.request, 'Zone deleted.')
        return super().form_valid(form)


class RouteListView(LoginRequiredMixin, ListView):
    model = Route
    template_name = 'core/route_list.html'
    context_object_name = 'routes'

    def get_queryset(self):
        return Route.objects.select_related('zone', 'zone__ward').all()


class RouteCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Route
    form_class = RouteForm
    template_name = 'core/route_form.html'
    success_url = reverse_lazy('core:route_list')

    def form_valid(self, form):
        messages.success(self.request, 'Route created.')
        return super().form_valid(form)


class RouteUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    template_name = 'core/route_form.html'
    context_object_name = 'route'
    success_url = reverse_lazy('core:route_list')

    def form_valid(self, form):
        messages.success(self.request, 'Route updated.')
        return super().form_valid(form)


class RouteDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Route
    template_name = 'core/route_confirm_delete.html'
    context_object_name = 'route'
    success_url = reverse_lazy('core:route_list')

    def form_valid(self, form):
        messages.success(self.request, 'Route deleted.')
        return super().form_valid(form)


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'core/cart_list.html'
    context_object_name = 'carts'

    def get_queryset(self):
        return Cart.objects.select_related('route').all()


class CartCreateView(AdminDashboardRequiredMixin, LoginRequiredMixin, CreateView):
    model = Cart
    form_class = CartForm
    template_name = 'core/cart_form.html'
    success_url = reverse_lazy('core:cart_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cart created.')
        return super().form_valid(form)


class CartUpdateView(AdminDashboardRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Cart
    form_class = CartForm
    template_name = 'core/cart_form.html'
    context_object_name = 'cart'
    success_url = reverse_lazy('core:cart_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cart updated.')
        return super().form_valid(form)


class CartDeleteView(AdminDashboardRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Cart
    template_name = 'core/cart_confirm_delete.html'
    context_object_name = 'cart'
    success_url = reverse_lazy('core:cart_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cart deleted.')
        return super().form_valid(form)


@admin_dashboard_required
def analytics_dashboard(request):
    """Graphical analytics: pie chart (bills status), line/bar (collections & revenue over time)."""
    from billing.models import LandlordBill, BillingCycle
    from collection_records.models import CollectionRecord, GarbageCollectionLog

    # Pie: bills by status (paid vs unpaid) for current cycle
    current_cycle = BillingCycle.objects.filter(is_closed=False).order_by('-year', '-month').first()
    if current_cycle:
        bills = LandlordBill.objects.filter(cycle=current_cycle)
        total_billed = bills.aggregate(t=Sum('amount'))['t'] or 0
        total_paid = bills.aggregate(t=Sum('amount_paid'))['t'] or 0
        pie_data = {
            'labels': ['Paid', 'Unpaid'],
            'values': [float(total_paid), float(total_billed - total_paid)],
        }
    else:
        pie_data = {'labels': ['Paid', 'Unpaid'], 'values': [0, 0]}

    # Last 6 months: revenue (payments) and collection count
    today = timezone.now().date()
    months_labels = []
    revenue_data = []
    collection_count_data = []
    for i in range(5, -1, -1):
        # approximate: 30 days per month back
        d = today - timedelta(days=30 * i)
        year, month = d.year, d.month
        months_labels.append(f'{year}-{month:02d}')
        cycle = BillingCycle.objects.filter(year=year, month=month).first()
        if cycle:
            rev = LandlordBill.objects.filter(cycle=cycle).aggregate(t=Sum('amount_paid'))['t'] or 0
            revenue_data.append(float(rev))
        else:
            revenue_data.append(0)
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        cnt = CollectionRecord.objects.filter(
            assignment__date__gte=start,
            assignment__date__lte=end,
        ).count()
        collection_count_data.append(cnt)

    # Garbage collection logs (casual labourer form) last 7 days
    week_ago = today - timedelta(days=7)
    garbage_log_count = GarbageCollectionLog.objects.filter(collection_date__gte=week_ago).count()

    context = {
        'pie_data': pie_data,
        'pie_labels_json': json.dumps(pie_data['labels']),
        'pie_values_json': json.dumps(pie_data['values']),
        'months_labels_json': json.dumps(months_labels),
        'revenue_data_json': json.dumps(revenue_data),
        'collection_count_data_json': json.dumps(collection_count_data),
        'current_cycle': current_cycle,
        'garbage_log_count': garbage_log_count,
    }
    return render(request, 'core/analytics_dashboard.html', context)
