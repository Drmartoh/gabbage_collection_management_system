# GCMS — Garbage Collection Management System

Production-ready web application for community-based waste management in **Karai Ward, Kiambu County, Kenya**.

## Features

- **Role-based access**: Super Admin, Operations Admin, Supervisor, Collector, **Casual Labourer**, Landlord, County Officer (read-only)
- **Core data**: Wards, zones, routes, carts
- **Properties**: Landlords, properties, tenants; per-property collection days (default Tue/Sat)
- **Billing**: Landlord-based monthly billing at **KES 100 per tenant**; **Arrears** view; **Expenses** (weekly/monthly); **Payroll** for casual labourers (Saturday)
- **Collections**: Route assignment, daily collection logging; **Casual labourers** and **zone rotation**; **Garbage collection log** (where, when, who, incident)
- **Incidents**: Photo uploads and GPS tagging
- **Analytics**: Pie and line/bar charts (bills status, revenue, collections)
- **Dashboards**: AGCBO admin dashboard and County officer (read-only) dashboard
- **Notifications**: In-app with unread badge; created on payment received; mark all as read
- **Auth**: Login, logout, **password reset** (email); audit log on login and key actions
- **Errors**: Custom **404** and **500** pages
- **SMS**: API-ready notification integration
- **Security**: Secure authentication, audit logs, no open redirect on logout
- **Reporting**: PDF and Excel export
- **UI**: Django templates with Bootstrap 5, **collapsible side menu**, **dark theme** toggle

## Quick start (local test)

**Windows (one-time setup):**
```cmd
cd gcms_project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
The project includes a `.env` file for local development. Then either:

**Option A – run script (migrates + seeds + asks for superuser if needed, then starts server):**
```cmd
run_local.bat
```

**Option B – manual:**
```cmd
python manage.py migrate
python manage.py seed_gcms
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and log in. Assign a **Role** to your user in Django Admin (**http://127.0.0.1:8000/admin/**).  
**Forgot password?** Use the “Forgot password?” link on the login page. In development, reset emails are printed to the console.

### If you get `InconsistentMigrationHistory`

This can happen if the DB was migrated before the `accounts` app had migrations. Reset and re-run:

```cmd
python manage.py reset_db --noinput
python manage.py seed_gcms
python manage.py createsuperuser
python manage.py runserver
```

Or manually: delete `db.sqlite3`, then run `migrate`, `seed_gcms`, `createsuperuser`.

## PythonAnywhere

See **[PYTHONANYWHERE.md](PYTHONANYWHERE.md)** for deployment steps. Summary: set `ALLOWED_HOSTS=yourusername.pythonanywhere.com` in `.env`, run `migrate` / `collectstatic`, and point the Web app WSGI to `gcms.wsgi`.

## Where to find features

| Feature | Where (after login) |
|--------|----------------------|
| **Dashboard** | Nav → Dashboard (admins) or County dashboard (county officer) |
| **Wards, Zones, Routes, Carts** | Nav → Wards, Zones, Routes, Carts |
| **Landlords** | Nav → Landlords |
| **Route assignments** | Nav → Assignments |
| **Billing & record payment** | Nav → Billing → “Record payment” on any bill with balance |
| **Incidents** | Nav → Incidents → “Report incident” to add one |
| **Reports (PDF/Excel)** | Nav → Reports |
| **Audit log** | Nav → Audit log |
| **Notifications** | Nav → Notifications |
| **My Properties / My Bills** | For Landlord role: Nav → My Properties, My Bills |
| **My Collections** | For Collector role: Nav → My Collections |
| **Analytics** (charts) | Nav → Menu → Analytics |
| **Arrears** (pending balances) | Nav → Menu → Arrears |
| **Expenses & Payroll** | Nav → Menu → Expenses, Payroll |
| **Labourers, Rotation, Collection log** | Nav → Menu → Labourers, Rotation, Collection log |
| **Django Admin** (users, roles, all data) | **http://127.0.0.1:8000/admin/** |

**Error log:** Application and request errors are written to `logs/gcms.log` (folder is created automatically when the app runs).

## Project structure

```
gcms_project/
  gcms/           # project settings, urls
  accounts/       # User, Role, AuditLog, auth
  core/           # Ward, Zone, Route, Cart
  properties/     # Landlord, Property, Tenant
  collections/    # RouteAssignment, CollectionRecord
  billing/        # BillingCycle, LandlordBill, PaymentRecord
  incidents/      # IncidentReport, IncidentPhoto
  notifications/  # Notification, SMSLog, send_sms()
  reports/        # County dashboard, PDF/Excel export
  templates/      # Base and app templates (Bootstrap 5)
```

## Roles

| Role              | Access |
|-------------------|--------|
| Super Admin       | Full access, admin dashboard |
| Operations Admin  | Operations, routes, assignments, billing |
| Supervisor        | Verify collections, view operations |
| Collector         | Collector dashboard, log collections (with GPS) |
| Landlord          | My properties, my bills |
| Casual Labourer   | Log collection (where, when, who, incident); view my logs |
| County Officer    | Read-only county dashboard and reports |

## Billing

- **Rate**: KES 100 per tenant per month (configurable via `GCMS_RATE_PER_TENANT_MONTHLY`).
- Generate bills: `python manage.py generate_monthly_bills YEAR MONTH`
- Seed data creates a sample cycle and bill.

## SMS

Set in `.env`:

- `GCMS_SMS_API_URL` — provider endpoint
- `GCMS_SMS_API_KEY` — API key
- `GCMS_SMS_SENDER_ID` — Sender ID (default GCMS)

Use `notifications.services.send_sms(recipient, message)` in code.

## Production

- Set `DEBUG=False`, strong `SECRET_KEY`, and `ALLOWED_HOSTS`.
- Use PostgreSQL: `DATABASE_URL=psql://user:pass@host/dbname`
- Static: `python manage.py collectstatic`
- Serve with gunicorn + whitenoise (or reverse proxy).

## License

Internal use — Karai Ward, Kiambu County.
