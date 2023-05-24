from django.contrib import admin

from apps.payments.models import Payment, Plan, Gateway, Currency


class PaymentAdmin(admin.ModelAdmin):
    inlines = []
    fieldsets = (
        ('General', {'fields': ('ref_id', 'user', 'plan',
                                'gateway', 'created', 'updated',)}),
    )
    list_display = ('ref_id', 'user', 'plan', 'gateway', 'created', 'updated')
    search_fields = ('ref_id', 'user__email')
    list_filter = ('plan',)
    ordering = ('created',)
    readonly_fields = ['ref_id', 'created', 'updated']


class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'currency', 'limit', 'description', 'created', 'updated',)
    readonly_fields = ['created', 'updated']


class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created', 'updated',)
    list_filter = ('active',)
    ordering = ('-active',)
    readonly_fields = ['created', 'updated']


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created', 'updated',)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Gateway, PaymentGatewayAdmin)
admin.site.register(Currency, CurrencyAdmin)
