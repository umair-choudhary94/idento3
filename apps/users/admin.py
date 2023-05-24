from django.contrib import admin
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from apps.dashboard.forms import CustomerCreationForm, CustomerChangeForm, EmployeeCreationForm, EmployeeChangeForm
from apps.dashboard.models import Employee
from apps.users.forms import UserChangeForm, UserCreationForm
from apps.users.models import Company, Country, Identity
from apps.web.models import SiteSetting

User = get_user_model()


class UserAdminInline(admin.StackedInline):
    model = User
    extra = 1


class IdentityAdminInline(admin.StackedInline):
    model = Identity
    extra = 0
    min_num = 0
    max_num = 1


class UserAdmin(auth_admin.UserAdmin):
    inlines = [IdentityAdminInline]
    fieldsets = (
        (
            'General',
            {'fields': ('email', 'type', 'company_name', 'country', 'last_login', 'date_joined', 'is_active',)}),
        ('Profile', {'fields': ('name', 'address', 'tel', 'picture')}),
        ('Security', {'fields': ('is_superuser', 'groups', 'user_permissions', 'password')}),
        ('Settings', {'fields': ('logo',)}),
    )
    

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name', 'type', 'company_name',
                    'date_joined', 'is_superuser', 'is_active',
                    'profile_picture',"Initiate_ID",'verification_status')
    search_fields = ('name', 'email')
    list_filter = ('type', 'is_superuser', 'is_active',)
    ordering = ('-date_joined',)
    form = UserChangeForm
    add_form = UserCreationForm
    readonly_fields = ['date_joined', 'last_login', 'profile_picture', 'get_document','display_verification_score']

    class Media:
        js = ('dashboard/js/verification.js',)
    def display_verification_score(self, obj):
        # Calculate the verification score for the user
        risk_score = obj.calculate_verification_risk_score()

        # Define the risk score ranges and corresponding status, color, and tick mark
        ranges = [
            {'min': 81, 'max': 100, 'status': 'Very high', 'color': 'danger', 'tick': '✔'},
            {'min': 61, 'max': 80, 'status': 'High', 'color': 'warning', 'tick': '✔'},
            {'min': 41, 'max': 60, 'status': 'Moderate', 'color': 'secondary', 'tick': '✔'},
            {'min': 21, 'max': 40, 'status': 'Low', 'color': 'info', 'tick': '✔'},
            {'min': 0, 'max': 20, 'status': 'Very low', 'color': 'success', 'tick': '✔'}
        ]

        # Generate the HTML code for the table
        html = '<table class="table">'
        html += '<thead>'
        html += '<tr>'
        html += '<th>Range</th>'
        html += '<th>Status</th>'
        html += '</tr>'
        html += '</thead>'
        html += '<tbody>'

        # Iterate over the risk score ranges
        for range_data in ranges:
            min_value = range_data['min']
            max_value = range_data['max']
            status = range_data['status']
            color = range_data['color']
            tick = range_data['tick']

            # Determine if the risk score falls within the range
            if min_value <= risk_score <= max_value:
                tick_mark = tick
            else:
                tick_mark = ''

            # Generate the HTML row for the range
            html += f'<tr>'
            html += f'<td><span class="badge bg-{color}">{min_value}-{max_value}</span> {tick_mark}</td>'
            html += f'<td>{status}</td>'
            html += f'</tr>'

        html += '</tbody>'
        html += '</table>'

        return format_html(html)




    display_verification_score.short_description = 'Risk Score'  # Custom name for the display_verification_score field

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # Append the verification score fieldset to the existing fieldsets
        verification_fieldset = (
            'Risk Score', {
                'fields': ('display_verification_score',),
            },
        )
        fieldsets += (verification_fieldset,)

        return fieldsets

    def verification_status(self, obj):
        
        status = obj.identity.status
        if status == obj.identity.STATUS_VERIFIED:
            return format_html('<b style="color:green;">Verified &#10004;</b>')
        elif status == obj.identity.STATUS_NOT_VERIFIED:
                return format_html('<b style="color:red;">Not Verified &#10008;</b>')
        else:
            return format_html('<b>{}</b>', status)
        # except:
        #     return format_html(
        #         f'<a id="initiate_{obj.id}" class="btn btn-info" value="{obj.email}"'
        #         f'onclick="initiateVerification({obj.id})" '
        #         f'href="#">Initiate ID Check</a>', 'url'
        #     )

    verification_status.short_description = 'Verification Status'
    def Initiate_ID(self, obj):
        return format_html(
                f'<a id="initiate_{obj.id}" class="btn btn-sm btn-info" value="{obj.email}"'
                f'onclick="initiateVerification({obj.id})" '
                f'href="#">ID Check</a>', 'url'
            )

    Initiate_ID.short_description = 'Initiate ID'
    def verification_score(self, obj):
        # Calculate the verification score for the user
        risk_score = obj.calculate_verification_risk_score()

        # You can customize the formatting of the verification score display if needed
        return f'{risk_score}'

    verification_score.short_description = 'Verification Score'  # Custom name for the verification_score field


    def profile_picture(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.picture.url))

    profile_picture.short_description = ' '

    def get_inline_instances(self, request, obj=None):
        return obj and super(UserAdmin, self).get_inline_instances(request, obj) or []

    @admin.display(ordering='user__identity__document', description='Document')
    def get_document(self, obj):
        if obj.identity:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.identity.document.url))

    @admin.display(ordering='identity__selfie', description='Selfie')
    def get_selfie(self, obj):
        if obj.identity:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.identity.selfie.url))

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # from apps.dashboard.models import Customer
        # from apps.dashboard.models import Employee
        # customers = list(Customer.objects.values_list('user', flat=True))
        # employees = list(Employee.objects.values_list('user', flat=True))
        # user_ids = customers + employees
        # if request.user.is_superuser:
        #     qs = qs.exclude(id__in=user_ids) # FIXME
        return qs

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        super().save_model(request, obj, form, change)
        if not obj.is_limited:
            obj.add_manager_permissions()

    def has_add_permission(self, request, obj=None):
        return not request.user.is_limited

    def has_delete_permission(self, request, obj=None):
        return not request.user.is_limited

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields.append('email')
        return readonly_fields


class BasePersonAdmin(admin.ModelAdmin):
    exclude = ['user', 'added_by']

    list_display = ('get_name', 'get_email', 'profile_picture',
                    'created', 'get_identity_number', 'verification_status')
    # list_filter = ('user__type',)
    readonly_fields = ['get_identity_number', 'get_document_type', 'get_document', 'get_selfie',
                       'get_verification_reason', 'verification_status']

    class Media:
        js = ('dashboard/js/verification.js',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(added_by=request.user)

    def profile_picture(self, obj):
        if obj.user.picture:
            url = obj.user.picture.url
            if not url.startswith('/profile_pictures'):
                url = f'/profile_pictures{url}'
            return format_html('<img src="{}" width="50" height="50"/>'.format(url))

    profile_picture.short_description = 'Profile Picture'

    def get_form(self, request, obj=None, **kwargs):
        form = super(BasePersonAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def verification_status(self, obj):
        try:
            return obj.user.identity.status
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
        if obj.user:
            return obj.user.name

    @admin.display(ordering='user__type', description='Type')
    def get_type(self, obj):

        if obj.user:
            return obj.user.type

    @admin.display(ordering='user__picture', description='Picture')
    def get_picture(self, obj):
        if obj.user:
            return obj.user.picture

    @admin.display(ordering='user__identity__status', description='Identification Status')
    def get_identity_status(self, obj):
        if obj.user: return obj.user.identity_status

    @admin.display(ordering='user__identity_serial_number', description='Verification Number')
    def get_identity_number(self, obj):
        if obj.user.identity:
            return obj.user.identity.serial_number

    @admin.display(ordering='user__identity__document_type', description='Document Type')
    def get_document_type(self, obj):
        if obj.user.identity:
            return obj.user.identity.document_type

    @admin.display(ordering='user__identity__document', description='Document')
    def get_document(self, obj):
        try:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.user.identity.selfie.url))
        except:
            return

    @admin.display(ordering='user__identity__selfie', description='Selfie')
    def get_selfie(self, obj):
        try:
            return format_html('<img src="{}" width="50" height="50"/>'.format(obj.user.identity.selfie.url))

        except:
            return

    @admin.display(description='Verification Reason')
    def get_verification_reason(self, obj):
        return ''

    def has_add_permission(self, request, obj=None):
        return request.user.has_paid_plan()

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_add_permission(request, obj)


class CompanyAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    list_display = ['country', 'get_country_flag']

    def get_country_flag(self, obj):
        return format_html('<img src="{}" width="40" height="25"/>'.format(obj.country.flag))


class IdentityAdmin(admin.ModelAdmin):
    inlines = []
    list_display = ('name', 'serial_number', 'verification_reason',
                    'document_type', 'get_document', 'get_selfie',
                    'status', 'created', 'updated')
    exclude = []
    search_fields = ('serial_number', 'name',)
    list_filter = ('status', 'verification_reason', 'document_type')
    fieldsets = (
        ('General', {'fields': ('name', 'temp_document', 'serial_number', 'document_type',
                                'verification_reason', 'status',
                                'created', 'updated')}),
        ('Files', {'fields': ('document', 'selfie',)}),
    )
    readonly_fields = ['created', 'updated', 'get_document', 'get_selfie']

    @admin.display(ordering='user__identity__document', description='Document')
    def get_document(self, obj):
        try:
            return format_html('<a href="{}" download target="_blank">Download</a> | <a href="{}" target="_blank"><img src="{}" width="50" height="50"/></a>'.format(obj.document.url, obj.document.url, obj.document.url))
        except:
            return

    @admin.display(ordering='identity__selfie', description='Selfie')
    def get_selfie(self, obj):
        try:
            return format_html('<a href="{}" download target="_blank">Download</a> | <a href="{}" target="_blank"><img src="{}" width="50" height="50"/></a>'.format(obj.selfie.url, obj.selfie.url, obj.selfie.url))
        except:
            return



class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['website_title', 'meta', 'keyword', 'logo', 'icon']

    def has_add_permission(self, request):
        retVal = super().has_add_permission(request)
        if retVal and SiteSetting.objects.exists():
            retVal = False
        return retVal


class EmployeeAdmin(BasePersonAdmin):
    change_list_template = "dashboard/employee_change_list.html"

    def has_add_permission(self, request, obj=None):
        return True

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


admin.site.register(User, UserAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Identity, IdentityAdmin)
admin.site.register(SiteSetting, SiteSettingAdmin)
