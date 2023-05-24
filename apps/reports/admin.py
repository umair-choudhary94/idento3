from django.contrib import admin

from apps.dashboard.models import Report


class ReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/reports.html'


admin.site.register(Report, ReportAdmin)
