"""Reports: county dashboard (read-only), PDF/Excel export."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone
from accounts.decorators import county_or_admin_required, admin_dashboard_required
from core.models import Ward, Zone, Route
from properties.models import Property
from collection_records.models import CollectionRecord, RouteAssignment
from billing.models import LandlordBill, BillingCycle
from incidents.models import IncidentReport
from django.db.models import Sum, Count


@county_or_admin_required
def county_dashboard(request):
    """County officer read-only dashboard."""
    today = timezone.now().date()
    wards = Ward.objects.filter(is_active=True).count()
    routes = Route.objects.filter(is_active=True).count()
    properties = Property.objects.filter(is_active=True).count()
    current_cycle = BillingCycle.objects.filter(is_closed=False).order_by('-year', '-month').first()
    total_billed = LandlordBill.objects.filter(cycle=current_cycle).aggregate(t=Sum('amount'))['t'] or 0
    total_paid = LandlordBill.objects.filter(cycle=current_cycle).aggregate(t=Sum('amount_paid'))['t'] or 0
    open_incidents = IncidentReport.objects.exclude(status__in=('resolved', 'closed')).count()
    today_collections = CollectionRecord.objects.filter(assignment__date=today).count()
    context = {
        'wards': wards, 'routes': routes, 'properties': properties,
        'current_cycle': current_cycle, 'total_billed': total_billed, 'total_paid': total_paid,
        'open_incidents': open_incidents, 'today_collections': today_collections,
    }
    return render(request, 'reports/county_dashboard.html', context)


@admin_dashboard_required
def export_menu(request):
    return render(request, 'reports/export_menu.html')


def _pdf_response(filename):
    resp = HttpResponse(content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def _excel_response(filename):
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@admin_dashboard_required
def export_collections_pdf(request):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
    except ImportError:
        return HttpResponse('PDF export requires reportlab. pip install reportlab', status=501)
    date_from = request.GET.get('from') or timezone.now().date().isoformat()
    date_to = request.GET.get('to') or timezone.now().date().isoformat()
    qs = CollectionRecord.objects.filter(
        assignment__date__gte=date_from,
        assignment__date__lte=date_to
    ).select_related('property', 'assignment', 'assignment__route')[:100]
    buf = __import__('io').BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, A4[1]-2*cm, "GCMS - Collection Report")
    p.drawString(2*cm, A4[1]-2.5*cm, "From %s to %s" % (date_from, date_to))
    y = A4[1] - 3.5*cm
    for r in qs:
        p.drawString(2*cm, y, "%s | %s | %s" % (r.assignment.date, r.property.name, r.get_status_display()))
        y -= 0.5*cm
        if y < 2*cm:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = A4[1] - 2*cm
    p.save()
    buf.seek(0)
    resp = HttpResponse(buf.read(), content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="collections_report.pdf"'
    return resp


@admin_dashboard_required
def export_billing_excel(request):
    try:
        import openpyxl
    except ImportError:
        return HttpResponse('Excel export requires openpyxl. pip install openpyxl', status=501)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bills"
    ws.append(["Landlord", "Cycle", "Tenants", "Amount", "Paid", "Balance"])
    for row in LandlordBill.objects.select_related('landlord', 'cycle').order_by('-cycle__year', '-cycle__month')[:500]:
        ws.append([
            row.landlord.full_name,
            str(row.cycle),
            row.tenant_count,
            float(row.amount),
            float(row.amount_paid),
            float(row.amount - row.amount_paid),
        ])
    buf = __import__('io').BytesIO()
    wb.save(buf)
    buf.seek(0)
    resp = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="billing_export.xlsx"'
    return resp


@admin_dashboard_required
def export_incidents_excel(request):
    try:
        import openpyxl
    except ImportError:
        return HttpResponse('Excel export requires openpyxl. pip install openpyxl', status=501)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Incidents"
    ws.append(["Title", "Property", "Severity", "Status", "Reported"])
    for row in IncidentReport.objects.select_related('property').order_by('-reported_at')[:500]:
        ws.append([
            row.title,
            str(row.property) if row.property else "",
            row.get_severity_display(),
            row.get_status_display(),
            row.reported_at.strftime("%Y-%m-%d %H:%M"),
        ])
    buf = __import__('io').BytesIO()
    wb.save(buf)
    buf.seek(0)
    resp = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="incidents_export.xlsx"'
    return resp
