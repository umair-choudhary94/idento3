from django.contrib import admin
from django.contrib.admin import AdminSite

from apps.dashboard.admin import EmployeeAdmin
from apps.dashboard.models import Employee


# Register your models here.

class LimitedAdminSite(AdminSite):
    site_header = "Limited Dashboard"
    site_title = "Limited Dashboard"
    index_title = "Limited Dashboard"


limited_dashboard_site = LimitedAdminSite(name='limited_dashboard_admin')

# limited_dashboard_site.register(Employee, EmployeeAdmin)
