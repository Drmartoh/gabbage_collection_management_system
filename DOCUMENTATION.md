# GCMS — Garbage Collection Management System

## Comprehensive System Documentation

**Version:** 1.0  
**Target:** Karai Ward, Kikuyu Constituency, Kiambu County, Kenya  
**Purpose:** End-to-end management of waste collection operations, landlord billing, collection logging, incidents, and reporting for a ward-level garbage collection body (AGCBO).

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [User Roles and Access Control](#4-user-roles-and-access-control)
5. [Data Model](#5-data-model)
6. [Application Modules](#6-application-modules)
7. [Maps and Location](#7-maps-and-location)
8. [Integrations (HERE, SMS, Email)](#8-integrations-here-sms-email)
9. [Configuration and Environment](#9-configuration-and-environment)
10. [Key Workflows](#10-key-workflows)
11. [Installation and Running](#11-installation-and-running)
12. [Testing](#12-testing)
13. [Deployment Notes](#13-deployment-notes)
14. [File and Folder Structure](#14-file-and-folder-structure)
15. [Audit Events](#15-audit-events)

---

## 1. Introduction

### 1.1 What is GCMS?

GCMS is a web application for managing **garbage collection** in a defined geographic area (ward). It supports:

- **Administration:** Wards, zones, routes, carts, landlords, properties, tenants.
- **Billing:** Monthly bills per landlord (based on tenant count at KES 100 per tenant), payment recording, arrears, expenses, and payroll for casual labourers.
- **Collection operations:** Assigning collectors and carts to routes, logging collections (with optional GPS), supervisor verification, and casual labourer logs (where, when, who, incident).
- **Incidents:** Reporting and tracking incidents with photos and GPS, severity and status.
- **Maps and location:** Live maps (ward map, properties heat map, route map), address autocomplete for landlords and properties, routing and nearby places (HERE).
- **Notifications:** In-app notifications and optional SMS on payment.
- **Reports and audit:** Exports (PDF, Excel), audit log, county read-only dashboard.

### 1.2 Key Concepts

- **Ward / Zone / Route:** Geographic hierarchy. A **Ward** (e.g. Karai Ward) contains **Zones**; each Zone has **Routes** (collection routes). **Carts** (physical waste carts) can be assigned to routes.
- **Landlord / Property / Tenant:** A **Landlord** has one or more **Properties**; each **Property** has **Tenants**. Billing is per landlord per month: **bill amount = tenant_count × rate** (default rate KES 100 per tenant per month).
- **Billing cycle:** A month (year–month). Bills are generated per landlord for a cycle; payments are recorded against bills; **balance = amount − amount_paid**.
- **Collection:** **Route assignments** assign a collector (user) and optionally a cart to a route for a given date. **Collection records** are per property per assignment (status: pending → collected → verified). **Garbage collection logs** are filled by casual labourers (property, date, time, landlord, incident/notes).

---

## 2. Technology Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | Django 5.x, Python 3.x |
| Database    | SQLite (default), PostgreSQL (production via `DATABASE_URL`) |
| Frontend    | HTML, Bootstrap 5, Bootstrap Icons, vanilla JavaScript |
| Forms       | Django forms, django-crispy-forms (Bootstrap 5) |
| Static      | WhiteNoise (production), `collectstatic` |
| Maps / Geo  | HERE Maps JavaScript API 3.1, HERE Geocoding & Search, HERE Routing API v8, HERE Autosuggest |
| Email       | Django email (console in DEBUG; SMTP in production) |
| SMS         | Optional REST API (e.g. Africa's Talking, Twilio) via `notifications.services.send_sms` |
| Auth        | Django auth, custom `User` with `Role` FK |

---

## 3. System Architecture

### 3.1 URL Structure

| Prefix       | App            | Purpose |
|-------------|----------------|--------|
| `/`         | accounts       | Login, logout, dashboard redirect, password reset |
| `/core/`    | core           | Admin dashboard, analytics, settings, ward map, properties map, wards, zones, routes, carts |
| `/properties/` | properties   | Landlords, properties, tenants, landlord dashboard |
| `/collections/` | collection_records | Assignments, collector dashboard, log collection, verify, labourers, rotation, garbage log |
| `/billing/` | billing        | Bills, cycles, generate bills, record payment, arrears, expenses, payroll |
| `/incidents/` | incidents    | Incident list, create, detail, edit, delete |
| `/notifications/` | notifications | Notification list, mark read, mark all read |
| `/reports/` | reports        | Export menu, county dashboard, audit log, PDF/Excel exports |
| `/admin/`   | Django admin   | Full data and user/role management |

### 3.2 Django Apps

- **accounts:** User (extends AbstractUser), Role, AuditLog; User has `first_login_tour_done` and `walkthrough_page_tips_seen` for in-app training; login/logout, password reset, dashboard redirect; middleware for role requirement.
- **core:** Ward, Zone, Route, Cart, **SystemSetting** (key-value for e.g. walkthrough_enabled); admin dashboard, analytics, settings (including in-app training toggle), maps (ward map, properties heat map, route map); walkthrough API (mark welcome done, mark page tip seen).
- **properties:** Landlord, Property, PropertyCollectionDay, Tenant; CRUD and landlord dashboard.
- **collection_records:** RouteAssignment, CollectionRecord, CasualLabourer, LabourerZoneRotation, GarbageCollectionLog; assignments, collector flow, labourers, rotation, garbage log.
- **billing:** BillingCycle, LandlordBill, PaymentRecord, ExpenseType, Expense, LabourerPayment; cycles, bills, payments, arrears, expenses, payroll.
- **incidents:** IncidentReport, IncidentPhoto; incident CRUD with photos and GPS.
- **notifications:** Notification, SMSLog; in-app notifications and SMS service.
- **reports:** No models; exports and county dashboard using other apps’ data; audit log view.

### 3.3 Middleware

- **RoleRequiredMiddleware:** If the user is authenticated but has no `role`, redirect to `pending_role` except for login, logout, dashboard, password-reset, and admin paths.

### 3.4 Context Processors

- **gcms_settings:** Exposes `GCMS_RATE_PER_TENANT`, `GCMS_SITE_NAME`, `GCMS_WARD`, `GCMS_COUNTY`, `HERE_API_KEY` (non-sensitive) to templates. `HERE_API_KEY` is read from **core.SystemSetting** (Settings page) first, then from `.env`/settings.
- **gcms_notification_count:** Exposes `gcms_unread_notifications` for the current user.
- **gcms_walkthrough:** Exposes `gcms_walkthrough_enabled`, `gcms_show_welcome_tour`, `gcms_show_walkthrough_tip`, `gcms_walkthrough_tip`, `gcms_walkthrough_page_slug` for in-app training (first-login welcome and per-page tips).

---

## 4. User Roles and Access Control

### 4.1 Roles (accounts.Role)

| Role              | Description              | Access |
|-------------------|--------------------------|--------|
| super_admin       | Full system access       | All features + Django admin |
| operations_admin  | Day-to-day operations    | Same as supervisor (admin dashboard, all ops) |
| supervisor        | Supervise collections    | Admin dashboard, assignments, verify collections, labourers, rotation, garbage log, incidents, billing, reports, notifications |
| collector         | Field collector          | Collector dashboard, log collection for assigned routes |
| casual_labourer   | Casual worker            | Garbage log list and create only (optionally scoped to own logs) |
| landlord          | Property owner           | Landlord dashboard (own properties), my bills, notifications |
| county_officer    | Read-only (e.g. county)  | County dashboard, reports, notifications; no create/edit/delete |

### 4.2 Dashboard Redirect (by role)

- **super_admin / operations_admin / supervisor** → `core:admin_dashboard`
- **county_officer** → `reports:county_dashboard`
- **collector** → `collections:collector_dashboard`
- **landlord** → `properties:landlord_dashboard`
- **casual_labourer** → `collections:garbage_log_list`
- No role → `accounts:pending_role`

### 4.3 Decorators / Mixins

- **@admin_dashboard_required:** Restricts to admin roles (super_admin, operations_admin, supervisor).
- **@county_or_admin_required:** Allows county_officer or admin roles.
- **@role_required(role_name):** Restricts to that role (e.g. collector for log_collection).
- **AdminDashboardRequiredMixin:** Class-based equivalent of admin_dashboard_required.

---

## 5. Data Model

### 5.1 Accounts

- **Role:** name (e.g. super_admin, landlord), description, is_read_only (county).
- **User (AUTH_USER_MODEL):** username, password, email, first_name, last_name, role (FK), phone, profile_updated_at, **first_login_tour_done**, **walkthrough_page_tips_seen** (JSON list of slugs for in-app tips). Methods: get_display_name(), is_super_admin, is_landlord, etc., can_edit().
- **AuditLog:** user, action (create/update/delete/login/export), model_name, object_id, object_repr, message, ip_address, created_at.

### 5.2 Core

- **SystemSetting:** key (unique), value, description, updated_at; class methods get_value(key, default), set_value(key, value, description).
- **Ward:** name, county, code, is_active.
- **Zone:** ward (FK), name, code, description, is_active.
- **Route:** zone (FK), name, code, description, day_of_week (0–6), is_active.
- **Cart:** code, route (FK, optional), status (active/maintenance/retired), notes.

### 5.3 Properties

- **Landlord:** user (OneToOne, optional), full_name, phone, email, id_number, address, latitude, longitude, is_active. Address is required on form; HERE autocomplete fills address + lat/lng.
- **Property:** landlord (FK), route (FK, optional), name, plot_number, physical_address, latitude, longitude, is_active. Has collection_days_display() (default Tue/Sat).
- **PropertyCollectionDay:** property (FK), day_of_week (0–6). Unique per (property, day_of_week).
- **Tenant:** property (FK), full_name, phone, is_active.

### 5.4 Billing

- **BillingCycle:** year, month, is_closed. Unique (year, month).
- **LandlordBill:** cycle (FK), landlord (FK), tenant_count, amount, amount_paid. balance = amount − amount_paid. Unique (cycle, landlord).
- **PaymentRecord:** bill (FK), amount, method (mpesa/bank/cash/cheque/other), reference, recorded_by. Signal updates LandlordBill.amount_paid on save/delete.
- **ExpenseType:** name, pay_frequency (weekly/monthly), is_active.
- **Expense:** expense_type (FK), amount, due_date, paid_at, vendor, reference, notes, recorded_by.
- **LabourerPayment:** labourer (FK to CasualLabourer), week_ending_date, amount, paid_at, reference, recorded_by. Unique (labourer, week_ending_date).

### 5.5 Collection Records

- **RouteAssignment:** route (FK), collector (User FK), cart (FK, optional), date, is_completed, notes. Unique (route, date).
- **CollectionRecord:** assignment (FK), property (FK), status (pending/collected/verified/skipped/issue), collected_at, latitude, longitude, notes, verified_by, verified_at, verification_notes.
- **CasualLabourer:** user (OneToOne, optional), full_name, phone, id_number, is_active.
- **LabourerZoneRotation:** labourer (FK), zone (FK), assigned_by, valid_from, valid_to, notes.
- **GarbageCollectionLog:** labourer (FK), property (FK), zone (FK, optional), collection_date, collection_time, landlord (FK, optional), incident_or_dispute, notes, recorded_by.

### 5.6 Incidents

- **IncidentReport:** reported_by, property (FK, optional), title, description, severity (low/medium/high/critical), status (open/in_progress/resolved/closed), latitude, longitude, reported_at, resolved_at.
- **IncidentPhoto:** incident (FK), image (upload_to=incidents/%Y/%m/), caption.

### 5.7 Notifications

- **Notification:** user (FK), title, message, link, is_read, created_at.
- **SMSLog:** recipient, message, status (pending/sent/failed), external_id, sent_at, error_message.

---

## 6. Application Modules

### 6.1 Accounts

- **Login:** GCMSLoginView; logs audit on success.
- **Logout:** GCMSLogoutView; GET allowed; redirect uses `?next=` only if safe (relative path, no `//`).
- **Password reset:** GCMSPasswordResetView → done → confirm (uidb64/token) → complete. Email templates in accounts/emails/.
- **Dashboard redirect:** Role-based (see 4.2).
- **Pending role:** Shown when user has no role.

### 6.2 Core

- **Admin dashboard:** Stats (wards, routes, properties, tenants, open incidents), today’s assignments, billing summary, quick access (Ward map, Properties map, Analytics, Settings, Notifications), and a full grid of feature cards (wards, zones, routes, carts, landlords, tenants, assignments, billing, cycles, incidents, analytics, properties map, settings, arrears, expenses, payroll, labourers, rotation, collection log, reports, audit, notifications, Django admin). Stat cards are clickable (wards → ward list, tenants → tenant list, etc.). Sidebar (admin/supervisor) includes Landlords, Tenants, Assignments, and other links.
- **Analytics dashboard:** Charts (e.g. pie: bill status, line: revenue, bar: collections) via Chart.js; data from view.
- **Settings (GCMS):** Site name, ward, county, billing rate, HERE configured (yes/no), SMS configured (yes/no), session hours, link to Django admin. **In-app training** can be toggled here (enable/disable first-login welcome and per-page tips). Stored in **core.SystemSetting** (`walkthrough_enabled`).
- **In-app training (walkthrough):** When enabled in Settings, (1) on **first login** the user sees a welcome modal (“Welcome to GCMS…”) with a “Get started” button; (2) the **first time** they open a section (e.g. Landlords, Billing, Assignments), a short **contextual tip** pop-up explains what that section does. Tips are defined in `core.walkthrough.TOUR_PAGES` (view name → slug, title, body). User state: `User.first_login_tour_done` and `User.walkthrough_page_tips_seen` (list of slugs). API: `POST /core/walkthrough/mark-welcome-done/`, `POST /core/walkthrough/mark-page-seen/` (body: `slug`) to mark completed; both require login.
- **Ward map:** Live HERE map centered on Kikuyu Constituency, Karai Ward (fixed center and zoom).
- **Properties map (heat map):** All properties with lat/lng; optional heat layer; click marker → detail panel (landlord, property, address, route, zone, tenants, link to property).
- **Route map:** Per-route map of properties with coordinates; “Show driving route” (HERE Routing v8), “Nearby places” (HERE Browse).
- **Wards / Zones / Routes / Carts:** Full CRUD (list, add, edit, delete).

### 6.3 Properties

- **Landlords:** List, add, edit, delete; detail view with properties list. **Add/Edit Landlord:** Address is required; HERE address autocomplete (as-you-type) fills address and optional lat/lng (stored on Landlord).
- **Properties:** Create (under a landlord), edit, delete, detail. Property form includes collection-days formset (PropertyCollectionDay). Address/location: HERE “Search location” to geocode and set physical_address, latitude, longitude. Property detail shows map if lat/lng present; “Nearby places (HERE)” optional.
- **Tenants:** **Tenant list** (`/properties/tenants/`, `properties:tenant_list`): all tenants with name, phone, house no., email, property, landlord, rate (standard or override), status; paginated. Add/edit/delete tenants from a property (Landlord → Property → Tenants). Tenant fields: full_name, phone, house_no, email (optional), monthly_rate (optional override), is_active. Billing uses standard rate (Settings) or per-tenant override; tenant count drives bill amount.

### 6.4 Billing

- **Billing cycles:** List, add, edit. **Generate bills:** For a cycle, creates or updates LandlordBill per landlord (amount = tenant_count × rate; tenant_count from active tenants at generation time).
- **Bills list:** All bills; link to record payment.
- **Record payment:** Form: amount, method, reference. Overpayment check: amount must be ≤ bill.balance. On success: PaymentRecord created, bill.amount_paid updated via signal, audit log, in-app notification for landlord user (if any), optional SMS to landlord.phone if SMS configured.
- **Arrears:** List of bills with balance > 0; total arrears and per-landlord totals.
- **Expenses:** List, add, edit; expense types (with pay_frequency); mark paid.
- **Payroll (labourers):** List, add LabourerPayment (labourer, week-ending date, amount, etc.).
- **My bills (landlord):** List of bills for the logged-in landlord (landlord_profile).

### 6.5 Collections

- **Route assignments:** List, add, edit, delete. Assign collector and optional cart to a route for a date.
- **Collector dashboard:** Assignments for the logged-in collector; link to “Log collection” per collection record.
- **Log collection (collector):** Form for a given CollectionRecord: optional GPS (lat/lon), “Get my location,” optional notes. Small HERE map (confirm map) shows property or current position. On submit: record marked collected, collected_at set, lat/lon and notes saved.
- **Verify collection (supervisor):** Mark a collection record as verified (verified_by, verified_at, notes).
- **Labourers:** CRUD for CasualLabourer.
- **Labourer rotation:** List, add, edit LabourerZoneRotation (labourer, zone, valid_from, valid_to).
- **Garbage log:** List (filtered by casual_labourer if that role); create form: labourer, property, zone, date, time, landlord, incident_or_dispute, notes. Optional HERE confirm map on log form.

### 6.6 Incidents

- **List, create, detail, edit, delete.** Create/Edit: inline photo formset (IncidentPhoto); form supports latitude/longitude (HERE “Search location” and “Get my location”). Detail shows map if lat/lng present.

### 6.7 Notifications

- **List:** Current user’s notifications (newest first).
- **Mark one read:** Open notification, mark read, optionally redirect to link.
- **Mark all read:** Set all current user’s notifications to read.

### 6.8 Reports

- **Export menu:** Links to collections PDF, billing Excel, incidents Excel.
- **County dashboard:** Read-only dashboard for county_officer.
- **Audit log:** List of AuditLog entries (admin).

---

## 7. Maps and Location

### 7.1 HERE Integration

- **API key:** Set in **Settings → HERE Maps** (saved in SystemSetting) or in `.env` as `HERE_API_KEY`. Value from Settings overrides .env. Used for Maps JavaScript API 3.1, Geocoding & Search (geocode, autosuggest), Routing API v8, Browse (nearby places).
- **Templates (templates/map/):**
  - **here_single_map.html:** Single marker map (lat, lng, optional label, height).
  - **here_multi_map.html:** Multiple markers, bounds fit.
  - **here_address_search.html:** Search box + “Search” button; geocode and fill address + lat/lng into form fields (used on property form, incident form).
  - **here_address_autocomplete.html:** As-you-type address suggestions (HERE Autosuggest); on select fills address + lat/lng (used on landlord form).
  - **here_confirm_map.html:** Small map that updates when lat/lng inputs change; optional initial center (e.g. property); used on collection log form.

### 7.2 Where Maps Are Used

- **Ward map:** Fixed map for Kikuyu Constituency, Karai Ward (`core:ward_map`).
- **Properties map:** Heat map + markers; click marker for landlord/property details (`core:properties_heatmap`).
- **Route map:** Per-route properties, driving route (HERE Routing), nearby places (`core:route_map`).
- **Property detail:** Single-marker map if property has lat/lng; “Nearby places (HERE).”
- **Incident detail:** Single-marker map if incident has lat/lng.
- **Landlord form:** Address autocomplete (mandatory location) and optional lat/lng.
- **Property form:** “Search location (HERE)” to set address and lat/lng; collection days formset.
- **Incident form:** “Search location (HERE)” and “Get my location” for lat/lng; photo formset.
- **Collection log:** Confirm map (property or current GPS).

---

## 8. Integrations (HERE, SMS, Email)

### 8.1 HERE

- **Maps:** `https://js.api.here.com/v3/3.1/mapsjs-core.js`, mapsjs-service.js, mapsjs-mapevents.js, mapsjs-ui.js, mapsjs-data.js (for heat map where used).
- **Geocoding:** `https://geocode.search.hereapi.com/v1/geocode?q=...&apikey=...`
- **Autosuggest:** `https://autosuggest.search.hereapi.com/v1/autosuggest?q=...&at=...&apikey=...&in=countryCode:KEN&limit=8`
- **Routing:** `https://router.hereapi.com/v8/routes?origin=...&destination=...&via=...&transportMode=car&return=polyline&apikey=...` (polyline decoded with flexible polyline for route map).
- **Browse (places):** `https://browse.search.hereapi.com/v1/browse?at=...&limit=...&apikey=...`

### 8.2 SMS

- **Service:** `notifications.services.send_sms(recipient, message)` creates an SMSLog and, if `GCMS_SMS_API_URL` and `GCMS_SMS_API_KEY` are set, POSTs to the configured API (payload adaptable for provider).
- **Usage:** After recording a payment, if landlord has phone and SMS is configured, an SMS is sent (e.g. “GCMS: Payment of KES X received. Balance: KES Y.”).

### 8.3 Email

- **Password reset:** Django’s PasswordResetView; templates in accounts/emails/. In DEBUG, emails are printed to console.
- **Production:** Configure EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.

---

## 9. Configuration and Environment

### 9.1 Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|--------|
| DEBUG | Debug mode | False |
| SECRET_KEY | Django secret | (required in production) |
| ALLOWED_HOSTS | Comma-separated hosts | localhost,127.0.0.1 |
| DATABASE_URL | Database URL | sqlite:///db.sqlite3 |
| SESSION_COOKIE_SECURE | Secure session cookie | not DEBUG |
| CSRF_COOKIE_SECURE | Secure CSRF cookie | not DEBUG |
| GCMS_SMS_API_URL | SMS API endpoint | '' |
| GCMS_SMS_API_KEY | SMS API key | '' |
| GCMS_SMS_SENDER_ID | SMS sender id | GCMS |
| HERE_API_KEY | HERE Maps/Geocoding/Routing key | '' |

### 9.2 Settings (gcms/settings.py)

- **Billing:** `GCMS_RATE_PER_TENANT_MONTHLY` = 100 (KES).
- **Session:** `SESSION_COOKIE_AGE` = 28800 (8 hours), `SESSION_SAVE_EVERY_REQUEST` = True.
- **Static:** WhiteNoise in production; `STATIC_ROOT` = staticfiles.
- **Media:** `MEDIA_URL` = media/, `MEDIA_ROOT` = media (incident photos, etc.).
- **Crispy:** Bootstrap 5.
- **Custom:** `AUTH_USER_MODEL` = 'accounts.User', `LOGIN_URL` = 'accounts:login', `LOGIN_REDIRECT_URL` = 'accounts:dashboard_redirect', `LOGOUT_REDIRECT_URL` = 'accounts:login'.

### 9.3 System settings (core.SystemSetting) and in-app training

- **SystemSetting** is a key-value model used for options editable from the GCMS Settings page. Keys used: **walkthrough_enabled** (value `true`/`false`), **billing_rate_per_tenant** (default fee in KES), **here_api_key** (HERE Maps API key; overrides .env when set). When `true`, in-app training is on: first-time users see a welcome modal, and the first time they visit each major page (Landlords, Billing, etc.) they see a short explanatory tip. Admins can turn this off via **Settings → In-app training → Enable/Disable → Save**.
- Tip content is defined in **core/walkthrough.py** (`TOUR_PAGES`: view name → slug, title, body). Covered views include admin_dashboard, analytics_dashboard, properties_heatmap, ward_map, route_list, landlord_list, **tenant_list**, landlord_detail, property_detail, assignment_list, collector_dashboard, labourer_list, garbage_log_list, bill_list, arrears_list, expense_list, labourer_payment_list, incident_list, notification_list, export_menu, audit_log, county_dashboard, ward_list, zone_list, cart_list, gcms_settings, landlord_dashboard, my_bills.

### 9.4 Handlers

- **404:** `gcms.views.page_not_found` (templates/404.html).
- **500:** `gcms.views.server_error` (templates/500.html).

(Previously “9.3 Handlers” is now 9.4.)

---

## 10. Key Workflows

### 10.1 Billing Cycle and Payments

1. Create a **Billing cycle** (e.g. 2025-02).
2. **Generate bills** for that cycle: for each landlord, create/update LandlordBill with tenant_count and amount = tenant_count × rate.
3. Landlords pay; staff **record payment** (amount, method, reference). Overpayment is rejected. PaymentRecord is created; signal updates LandlordBill.amount_paid; audit and notification (and optional SMS) run.
4. **Arrears** list shows all bills with balance > 0.

### 10.2 Collection (Collector Flow)

1. Supervisor creates **Route assignments** (route, collector, optional cart, date).
2. Collector opens **Collector dashboard**, sees assignments and list of collection records (properties) per assignment.
3. Collector clicks **Log collection** for a record: optionally captures GPS (“Get my location” or manual), sees confirm map, adds notes, submits. Record status → collected, collected_at and lat/lon saved.
4. Supervisor can **Verify collection** (verify view) to set verified_by and verified_at.

### 10.3 Casual Labourer and Garbage Log

1. Supervisor creates **Labourers** and **Labourer zone rotations** (labourer, zone, valid_from, valid_to).
2. Casual labourer (or staff) creates **Garbage collection logs**: labourer, property, date, time, landlord, incident/notes. Optional confirm map. Form can auto-fill landlord/zone from property.

### 10.4 Incidents

1. User creates **Incident** (title, description, severity, optional property, lat/lng via search or “Get my location”), optionally attaches **photos** (formset).
2. Incidents appear in list and detail; detail shows map if coordinates exist. Status can be updated (open → in_progress → resolved → closed).

### 10.5 Landlord and Property Setup

1. Add **Landlord** (required **address** via HERE autocomplete; optional lat/lng stored).
2. Add **Property** under landlord (name, route, optional address/lat/lng via “Search location,” optional **collection days** formset).
3. Add **Tenants** to property. Tenant count is used when generating bills.

---

## 11. Installation and Running

### 11.1 Requirements

- Python 3.10+
- pip, venv

### 11.2 Setup

```bash
cd gcms_project
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env: SECRET_KEY, optional HERE_API_KEY, SMS, DATABASE_URL
python manage.py migrate
python manage.py createsuperuser   # optional, for Django admin
# Optional: python manage.py run_seed   # if seed command exists
```

### 11.3 Run Development Server

```bash
python manage.py runserver
```

- App: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/

### 11.4 Static and Media (Production)

```bash
python manage.py collectstatic --noinput
```

Serve media files (e.g. incident photos) from `MEDIA_ROOT`; WhiteNoise serves static from `STATIC_ROOT`.

---

## 12. Testing

- **Accounts:** Login (GET, success, invalid), logout (redirect, safe next, empty next), password reset page.
- **Billing:** Overpayment rejected; valid payment updates bill balance (PaymentRecord + signal).
- **Notifications:** List requires login; list shows user notifications; mark one read; mark all read.

Run:

```bash
python manage.py test accounts.tests billing.tests notifications.tests
```

---

## 13. Deployment Notes

### Generating a SECRET_KEY

Never use a default or guessable value in production. Generate a new key and put it in `.env` as `SECRET_KEY=...`.

**Option 1 (Django):** Run in your project environment (with Django installed):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Option 2 (Python only):**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the printed string into your `.env` file, e.g. `SECRET_KEY=django-insecure-abc123...` or `SECRET_KEY=xyz789...`.

---

- Set **DEBUG=False**, strong **SECRET_KEY**, and **ALLOWED_HOSTS**.
- Use **PostgreSQL** (or another production DB) via **DATABASE_URL**.
- Configure **EMAIL_*** for password reset and any other emails.
- Optionally set **GCMS_SMS_*** for payment SMS.
- Set **HERE_API_KEY** for maps (Settings → HERE Maps or `.env`); restrict key by referrer in HERE developer portal.
- **SESSION_COOKIE_SECURE** and **CSRF_COOKIE_SECURE** true over HTTPS.
- Run **migrate** and **collectstatic**; use a production WSGI/ASGI server (e.g. Gunicorn + Nginx or PythonAnywhere).

**PythonAnywhere:** Clone the repo, create virtualenv, `pip install -r requirements.txt`, copy `.env.example` to `.env` and set `ALLOWED_HOSTS=gcmskarai.pythonanywhere.com` (or your PA subdomain), `DEBUG=False`, secure cookies. Generate `SECRET_KEY` as above. Run `migrate`, `collectstatic`, `createsuperuser`. In the Web tab set project path, virtualenv, and WSGI to Django (`gcms.wsgi`); add static URL `/static/` → `staticfiles`, `/media/` → `media`. Reload. See repo README or this doc for full steps.

---

## Quick Reference: Main URLs

| Name | URL (example) |
|------|----------------|
| Login | /login/ |
| Dashboard (redirect) | /dashboard/ |
| Admin dashboard | /core/ |
| Ward map | /core/ward-map/ |
| Properties map | /core/properties-map/ |
| Settings | /core/settings/ |
| Landlords | /properties/ |
| Tenants | /properties/tenants/ |
| Billing | /billing/ |
| Record payment | /billing/bill/<id>/pay/ |
| Assignments | /collections/ |
| Incidents | /incidents/ |
| Notifications | /notifications/ |
| Reports / Audit | /reports/, /reports/audit/ |
| Django admin | /admin/ |

---

---

## 14. File and Folder Structure

```
gcms_project/
├── gcms/                    # Project settings and root URL/config
│   ├── settings.py
│   ├── urls.py
│   ├── context_processors.py
│   ├── views.py             # 404, 500 handlers
│   └── admin_site.py        # Custom admin branding
├── accounts/                # Users, roles, auth, audit
│   ├── models.py            # User, Role, AuditLog
│   ├── views.py             # Login, logout, password reset, dashboard redirect
│   ├── urls.py
│   ├── middleware.py        # RoleRequiredMiddleware
│   ├── decorators.py        # admin_dashboard_required, role_required, etc.
│   ├── mixins.py
│   ├── utils.py             # log_audit
│   └── constants.py
├── core/                    # Wards, zones, routes, carts, dashboards, maps
│   ├── models.py
│   ├── views.py             # admin_dashboard, analytics, settings, ward_map, properties_heatmap, route_map, CRUD
│   ├── urls.py
│   └── forms.py
├── properties/              # Landlords, properties, tenants
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py             # LandlordForm (address autocomplete), PropertyForm, PropertyCollectionDayFormSet
├── collection_records/     # Assignments, collection records, labourers, garbage log
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── billing/                 # Cycles, bills, payments, expenses, payroll
│   ├── models.py            # Signals for amount_paid
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── incidents/               # Incident reports and photos
│   ├── models.py
│   ├── views.py             # Photo formset on create/update
│   ├── urls.py
│   └── (forms inline in views)
├── notifications/           # In-app notifications and SMS
│   ├── models.py
│   ├── views.py
│   ├── services.py          # send_sms
│   └── urls.py
├── reports/                 # Exports, county dashboard, audit
│   ├── views.py
│   ├── views_audit.py
│   └── urls.py
├── templates/
│   ├── base.html            # Layout, nav, theme toggle, sidebar
│   ├── breadcrumbs.html
│   ├── 404.html, 500.html
│   ├── accounts/            # login, password_reset_*
│   ├── core/                # admin_dashboard, analytics, settings, ward_map, properties_heatmap, route_map, CRUD
│   ├── map/                 # here_single_map, here_multi_map, here_address_search, here_address_autocomplete, here_confirm_map
│   ├── properties/          # landlord_*, property_*, tenant_*
│   ├── collections/         # assignment_*, log_collection, labourer_*, garbage_*
│   ├── billing/             # bill_list, record_payment, arrears, expense_*, payroll
│   ├── incidents/           # incident_list, incident_detail, incident_form
│   └── notifications/      # notification_list
├── media/                   # Uploaded files (e.g. incident photos)
├── static/                  # Project static (if any)
├── staticfiles/             # collectstatic output
├── .env, .env.example
├── requirements.txt
├── manage.py
└── DOCUMENTATION.md         # This file
```

---

## 15. Audit Events

The system logs the following to **AuditLog** (accounts.utils.log_audit):

| Action | When |
|--------|------|
| login | User logs in successfully (GCMSLoginView.form_valid) |
| create (PaymentRecord) | Payment recorded for a bill |
| create (generate bills) | Bills generated for a cycle |
| create (IncidentReport) | Incident created (with or without photos) |

Other critical actions (e.g. payment recording, bill generation) also trigger audit log entries where implemented. The **Audit log** report (reports:audit_log) lists these entries for admins.

---

*This documentation describes the GCMS system as implemented. For environment-specific or deployment details, refer to your deployment checklist and .env.example.*
