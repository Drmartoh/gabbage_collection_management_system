"""
In-app training: contextual tips per page (and first-login welcome).
Maps view names to slug, title, and body for the walkthrough popover.
"""
TOUR_PAGES = {
    'core:admin_dashboard': {
        'slug': 'admin_dashboard',
        'title': 'Admin Dashboard',
        'body': (
            'Your command centre. Here you see key stats at a glance: total landlords, properties, '
            'tenants, and collection progress. Use the menu to jump to Landlords, Billing, Collections, '
            'or Reports.'
        ),
    },
    'core:analytics_dashboard': {
        'slug': 'analytics',
        'title': 'Analytics',
        'body': (
            'Charts and trends for collections, billing, and incidents over time. Use this to spot '
            'patterns and report to the county.'
        ),
    },
    'core:properties_heatmap': {
        'slug': 'properties_map',
        'title': 'Properties Map',
        'body': (
            'All registered properties plotted on the ward map. Click a marker to see landlord and '
            'property details and quick links.'
        ),
    },
    'core:ward_map': {
        'slug': 'ward_map',
        'title': 'Ward Map',
        'body': (
            'Live map of Karai Ward and Kikuyu Constituency. Use it to orient routes and verify '
            'coverage.'
        ),
    },
    'core:route_list': {
        'slug': 'routes',
        'title': 'Routes',
        'body': (
            'Collection routes are tied to zones and have a day of the week. Each route can have '
            'carts assigned. Use these when assigning collectors and planning pickups.'
        ),
    },
    'properties:landlord_list': {
        'slug': 'landlords',
        'title': 'Landlords',
        'body': (
            'Landlords are property owners in the ward. Each landlord has a contact address (with map '
            'location), phone, and email. Add a landlord first, then add their properties and tenants. '
            'Billing is calculated per tenant per property.'
        ),
    },
    'properties:tenant_list': {
        'slug': 'tenants',
        'title': 'Tenants',
        'body': (
            'All tenants across properties. You see name, phone, house no., email, property, landlord, '
            'and rate (standard or per-tenant override). Add or edit tenants from a property (Landlords → Property → Tenants).'
        ),
    },
    'properties:landlord_detail': {
        'slug': 'landlord_detail',
        'title': 'Landlord Details',
        'body': (
            'View and edit this landlord, and manage their properties and tenants. You can add new '
            'properties from here.'
        ),
    },
    'properties:property_detail': {
        'slug': 'property_detail',
        'title': 'Property Details',
        'body': (
            'Each property belongs to a landlord and can be linked to a collection route and day. '
            'Tenant count here is used for monthly billing.'
        ),
    },
    'collection_records:assignment_list': {
        'slug': 'assignments',
        'title': 'Assignments',
        'body': (
            'Assign collectors and routes to specific dates. Collectors use their dashboard to see '
            'assignments and log each collection (with optional GPS confirmation).'
        ),
    },
    'collection_records:collector_dashboard': {
        'slug': 'collector_dashboard',
        'title': 'My Collections',
        'body': (
            'As a collector you see your assignments here. Open each assignment and log collections '
            'for each property; you can confirm location on the map.'
        ),
    },
    'collection_records:labourer_list': {
        'slug': 'labourers',
        'title': 'Labourers',
        'body': (
            'Casual labourers who assist with collection. They can be assigned to routes and their '
            'payments are tracked under Payroll.'
        ),
    },
    'collection_records:garbage_log_list': {
        'slug': 'garbage_log',
        'title': 'Collection Log',
        'body': (
            'Logs of garbage collected (e.g. bags or trips). Used by casual labourers to record '
            'their work for payroll.'
        ),
    },
    'billing:bill_list': {
        'slug': 'billing',
        'title': 'Billing',
        'body': (
            'Create billing cycles, generate bills for all properties (based on tenant count and rate), '
            'and record payments. Overpayments are handled automatically and can be applied to future bills.'
        ),
    },
    'billing:arrears_list': {
        'slug': 'arrears',
        'title': 'Arrears',
        'body': (
            'Landlords with outstanding balances. Use this list to follow up and record payments from '
            'the billing section.'
        ),
    },
    'billing:expense_list': {
        'slug': 'expenses',
        'title': 'Expenses',
        'body': (
            'Track operational expenses by type. Mark items as paid and use reports for financial '
            'overview.'
        ),
    },
    'billing:labourer_payment_list': {
        'slug': 'payroll',
        'title': 'Payroll',
        'body': (
            'Payments to casual labourers. Add payments and link them to labourers and periods; '
            'collection logs can inform amounts.'
        ),
    },
    'incidents:incident_list': {
        'slug': 'incidents',
        'title': 'Incidents',
        'body': (
            'Report and track incidents (e.g. missed collection, spill, complaint). Each incident '
            'can have photos and GPS location for follow-up.'
        ),
    },
    'notifications:notification_list': {
        'slug': 'notifications',
        'title': 'Notifications',
        'body': (
            'In-app notifications (e.g. payment received, assignment reminders). Mark as read or '
            'mark all read.'
        ),
    },
    'reports:export_menu': {
        'slug': 'reports',
        'title': 'Reports',
        'body': (
            'Export collections, billing, or incidents to PDF or Excel. County officers can also '
            'access the county dashboard from the menu.'
        ),
    },
    'reports:audit_log': {
        'slug': 'audit_log',
        'title': 'Audit Log',
        'body': (
            'History of important actions (logins, payments, bill generation, incident creation) for '
            'accountability and troubleshooting.'
        ),
    },
    'reports:county_dashboard': {
        'slug': 'county_dashboard',
        'title': 'County Dashboard',
        'body': (
            'Read-only overview for county officers: key metrics and links to exports.'
        ),
    },
    'core:ward_list': {
        'slug': 'wards',
        'title': 'Wards',
        'body': (
            'Wards within the county. Karai Ward is the primary ward; zones and routes belong to a ward.'
        ),
    },
    'core:zone_list': {
        'slug': 'zones',
        'title': 'Zones',
        'body': (
            'Zones divide the ward into collection areas. Each zone can have multiple routes.'
        ),
    },
    'core:cart_list': {
        'slug': 'carts',
        'title': 'Carts',
        'body': (
            'Physical waste collection carts. Assign them to routes and track status (active, '
            'maintenance, retired).'
        ),
    },
    'core:gcms_settings': {
        'slug': 'settings',
        'title': 'Settings',
        'body': (
            'View site name, ward, billing rate, and integrations (HERE Maps, SMS). You can turn '
            'in-app training on or off here so new users see helpful tips when they open each section.'
        ),
    },
    'properties:landlord_dashboard': {
        'slug': 'landlord_my_properties',
        'title': 'My Properties',
        'body': (
            'As a landlord you see your properties and can manage tenants. Your bills are under My Bills.'
        ),
    },
    'billing:my_bills': {
        'slug': 'my_bills',
        'title': 'My Bills',
        'body': (
            'View your bills and payment history. Pay at the office or via the instructed channels; '
            'payments will appear here once recorded.'
        ),
    },
}


def get_tip_for_view(view_name):
    """Return the tour tip dict for a view name, or None."""
    return TOUR_PAGES.get(view_name) if view_name else None
