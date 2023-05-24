from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from apps.dashboard.forms import CustomerCreationForm, CustomerChangeForm, EmployeeCreationForm, EmployeeChangeForm
from apps.dashboard.models import Employee, Customer, MyPlan, MyPayment, Profile, Report, Ticket, MyIdentity
from apps.users.admin import UserAdmin, BasePersonAdmin
from apps.web.views import LoginView

User = get_user_model()


class DashboardAdminSite(AdminSite):
    site_header = "Dashboard"
    site_title = "Dashboard"
    index_title = "Dashboard"
    index_template = "dashboard/index.html"

    def get_urls(self):
        urls = super(DashboardAdminSite, self).get_urls()
        dashboard_urls = [
            path('login/', LoginView.as_view(), name='login'),
        ]
        return dashboard_urls + urls


dashboard_admin_site = DashboardAdminSite(name='dashboard_admin')


class CustomerAdmin(BasePersonAdmin):
    change_list_template = "dashboard/customer_change_list.html"

    @admin.display(description='Verification Reason')
    def get_verification_reason(self, obj):
        return 'KYC'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.user.is_staff = True  # FIXME
        obj.user.add_limited_permissions()
        obj.user.save()

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'added_by')
        self.form = CustomerCreationForm
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('user', 'added_by')
        self.form = CustomerChangeForm

        return super(BasePersonAdmin, self).change_view(request, object_id)


class EmployeeAdmin(BasePersonAdmin):
    change_list_template = "dashboard/employee_change_list.html"

    @admin.display(description='Verification Reason')
    def get_verification_reason(self, obj):
        return 'Job'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.user.is_staff = True  # FIXME
        obj.user.add_limited_permissions()
        obj.user.save()

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'added_by')
        self.form = EmployeeCreationForm
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('user', 'added_by')
        self.form = EmployeeChangeForm

        return super(BasePersonAdmin, self).change_view(request, object_id)


class MyPlanAdmin(admin.ModelAdmin):
    change_list_template = "dashboard/plan_change_list.html"
    list_display = ('get_plan', 'total_credit', 'remaining_credit', 'created', 'updated')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    #
    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    @admin.display(ordering='payment__plan', description='Plan')
    def get_plan(self, obj):
        return obj.plan.title


class MyPaymentAdmin(admin.ModelAdmin):
    list_display = ('get_invoice_id', 'get_plan', 'get_amount', 'get_ref_id', 'created')
    fields = ['get_plan', 'get_amount', 'get_invoice_id', 'get_ref_id', 'created']
    readonly_fields = ['payment']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    @admin.display(ordering='payment__plan', description='Plan')
    def get_plan(self, obj):
        return obj.payment.plan.title

    @admin.display(ordering='payment__price', description='Price')
    def get_amount(self, obj):
        return f'{obj.payment.plan.price}{obj.payment.plan.currency.symbol}'

    @admin.display(ordering='payment__ref_id', description='Ref ID')
    def get_ref_id(self, obj):
        return obj.payment.ref_id

    @admin.display(ordering='payment__invoice_id', description='Invoice ID')
    def get_invoice_id(self, obj):
        return obj.payment.invoice_id

    @admin.display(ordering='payment__gateway', description='Payment Gateway')
    def get_gateway(self, obj):
        return obj.payment.gateway


class ProfileAdmin(UserAdmin):
    readonly_fields = ['date_joined', 'last_login', 'profile_picture', 'type']

    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/admin/sales/invoice')

    def response_change(self, request, obj):
        return redirect(reverse('dashboard_admin:dashboard_profile_change', kwargs={'object_id': obj.id}))

    def get_fieldsets(self, request, obj=None):
        if request.user.is_limited:
            fieldsets = (
                ('Profile', {'fields': ('name', 'email', 'address', 'tel', 'dob', 'picture')}),
                ('Account Info', {'fields': ('type', 'last_login', 'date_joined')}),
                ('Security', {'fields': ('password',)}),
            )
        else:
            fieldsets = (
                ('Profile', {'fields': ('name', 'email', 'address', 'tel', 'dob', 'picture', 'company_name', 'logo')}),
                ('Account Info', {'fields': ('type', 'last_login', 'date_joined')}),
                ('Security', {'fields': ('password',)}),
            )
        return fieldsets


class ReportAdmin(admin.ModelAdmin):
    change_list_template = 'dashboard/reports.html'


class MyTicketAdmin(admin.ModelAdmin):
    fields = ['title', 'text', ]
    list_display = ['title', 'assigned_to', 'status', 'created', 'updated', ]
    list_filter = ('status',)
    ordering = ('-status',)
    readonly_fields = ['created', 'updated', 'raised_by']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(raised_by=request.user)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.raised_by = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MyIdentityAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'serial_number', 'document_type', 'get_document', 'get_selfie',
                    'get_verification_reason', 'verification_status']
    fields = ['get_name', 'get_email', 'document_type', 'get_document', 'get_selfie',
              'get_verification_reason', 'verification_status', 'serial_number', 'created', 'updated']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def profile_picture(self, obj):
        if obj.user.picture:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.user.picture.url))

    profile_picture.short_description = ' '

    def get_form(self, request, obj=None, **kwargs):
        form = super(MyIdentityAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def verification_status(self, obj):
        try:
            return obj.status
        except:
            return format_html(
                f'<a type="button" id="initiate_{obj.user.id}" class="btn btn-info" value="{obj.user.email}"'
                f'onclick="initiateVerification({obj.user.id})" '
                f'>Initiate ID Check</a>', 'url'
            )

    verification_status.short_description = 'Verification Status'

    @admin.display(ordering='user__email', description='Email')
    def get_email(self, obj):
        if obj.user:
            return obj.user.email

    @admin.display(ordering='user__name', description='Name')
    def get_name(self, obj):
        return obj.user.name

    @admin.display(ordering='user__type', description='Type')
    def get_type(self, obj):
        return obj.user.type

    @admin.display(ordering='user__picture', description='Picture')
    def get_picture(self, obj):
        return obj.user.picture

    @admin.display(ordering='user__identity__status', description='Identification Status')
    def get_identity_status(self, obj):
        return obj.user.identity_status

    @admin.display(ordering='user__identity_serial_number', description='Verification Number')
    def get_identity_number(self, obj):
        return obj.serial_number

    @admin.display(ordering='user__identity__document_type', description='Document Type')
    def get_document_type(self, obj):
        return obj.document_type

    @admin.display(ordering='user__identity__document', description='Document')
    def get_document(self, obj):
        try:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.document.url))
        except:
            return

    @admin.display(ordering='user__identity__selfie', description='Selfie')
    def get_selfie(self, obj):
        try:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.selfie.url))
        except:
            return

    @admin.display(description='Verification Reason')
    def get_verification_reason(self, obj):
        return obj.verification_reason or 'KYC'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


dashboard_admin_site.register(Customer, CustomerAdmin)
dashboard_admin_site.register(Employee, EmployeeAdmin)
dashboard_admin_site.register(Ticket, MyTicketAdmin)
dashboard_admin_site.register(MyIdentity, MyIdentityAdmin)
dashboard_admin_site.register(MyPlan, MyPlanAdmin)
dashboard_admin_site.register(Report, ReportAdmin)
dashboard_admin_site.register(MyPayment, MyPaymentAdmin)
dashboard_admin_site.register(Profile, ProfileAdmin)
