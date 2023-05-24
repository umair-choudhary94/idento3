from django.contrib import admin

from apps.support.models import Ticket


class TicketAdmin(admin.ModelAdmin):
    fields = ['title', 'text', 'raised_by', 'assigned_to', 'status', 'created', 'updated', ]
    list_display = ['title', 'raised_by', 'assigned_to', 'status', 'created', 'updated', ]
    list_filter = ('status',)
    ordering = ('-status',)
    readonly_fields = ['created', 'updated', 'raised_by']

    # def has_add_permission(self, request):
    #     return not request.user.is_superuser


admin.site.register(Ticket, TicketAdmin)
