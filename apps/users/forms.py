from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, \
    PasswordResetForm as DjangoPasswordResetForm, SetPasswordForm as DjangoSetPasswordForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from apps.dashboard.models import MyPlan
from apps.payments.models import Plan
from apps.users.models import Country

User = get_user_model()


class RegisterForm(UserCreationForm):
    # country_choices = [[c.country.name, c.country.name] for c in Country.objects.all()]

    name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'autofocus'}), label='Name')
    email = forms.EmailField(widget=forms.EmailInput(), label='Email Address')
    username = forms.EmailField(widget=forms.EmailInput(), label='Username', required=False)
    address = forms.CharField(label='Address', required=False)
    country = CountryField(choices=[['aa', 'aa'], ['bb', 'bb']])
    tel = forms.CharField(label='Tel', required=False)
    type = forms.ChoiceField(required=False, choices=(
        ('Personal', 'Personal'),
        ('Company', 'Company')
    ))
    # plan = forms.HiddenInput()
    company_name = forms.CharField(label='Company Name', required=False)

    class Meta:
        model = User
        fields = (
            'name', 'email', 'tel', 'address', 'type', 'company_name', 'password1', 'password2',
        )

    def save(self, commit=True):
        user = super().save(commit)
        country = Country.objects.filter(country__name=self.data['country']).first()
        user.country = country
        user.save()
        return user


class LoginForm(AuthenticationForm):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    username = forms.CharField(required=False)

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        username_max_length = self.username_field.max_length or 254
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache


class PasswordResetForm(DjangoPasswordResetForm):
    def clean(self):
        super().clean()

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # print(f'{context["uid"]}/{context["token"]}/')
        user = User.objects.filter(email=self.cleaned_data['email']).first()
        if user:
            user.send_reset_password_email(context)


class SetPasswordForm(DjangoSetPasswordForm):
    pass
