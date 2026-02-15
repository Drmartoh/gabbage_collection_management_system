"""Role names for decorators and middleware."""
from accounts.models import Role

SUPER_ADMIN = Role.RoleName.SUPER_ADMIN
OPERATIONS_ADMIN = Role.RoleName.OPERATIONS_ADMIN
SUPERVISOR = Role.RoleName.SUPERVISOR
COLLECTOR = Role.RoleName.COLLECTOR
CASUAL_LABOURER = Role.RoleName.CASUAL_LABOURER
LANDLORD = Role.RoleName.LANDLORD
COUNTY_OFFICER = Role.RoleName.COUNTY_OFFICER

# Who can access admin-style dashboards (AGCBO)
ADMIN_ROLES = (SUPER_ADMIN, OPERATIONS_ADMIN, SUPERVISOR)
# County officer gets read-only dashboard
COUNTY_READ_ONLY = (COUNTY_OFFICER,)
