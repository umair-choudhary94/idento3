from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from apps.dashboard.models import Employee, Customer

User = get_user_model()


class BasePersonCreationForm(forms.ModelForm):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}), label='Name')
    email = forms.EmailField(label='Email')
    tel = forms.CharField(label='Tel', required=False)
    address = forms.CharField(label='Address', required=False)
    dob = forms.DateField(required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)

    error_messages = {
        'password_mismatch': 'The two password fields didn’t match.',
    }
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dob'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
            }
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists.')
        return email

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = User.objects.create(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            tel=self.cleaned_data['tel'],
            address=self.cleaned_data['address'],
            picture=self.cleaned_data['profile_picture'],
            dob=self.cleaned_data['dob'],
        )
        user.set_password(self.cleaned_data["password1"])
        user.save()

        person = super().save(commit=False)
        person.user = user
        person.added_by = self.current_user
        if commit:
            person.save()
        return person


class BasePersonChangeForm(forms.ModelForm):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}), label='Name')
    email = forms.EmailField(label='Email')
    tel = forms.CharField(label='Tel', required=False)
    dob = forms.DateField(label='Date of Birth', required=False)
    address = forms.CharField(label='Address', required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)

    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=
        'Raw passwords are not stored, so there is no way to see this '
        'user’s password, but you can change the password using '
        '<a href="{}">this form</a>.'
        ,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['dob'].widget = forms.widgets.DateInput(
            attrs={
                'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)',
                'class': 'form-control'
            }
        )
        if user:
            self.fields['name'].initial = user.name
            self.fields['email'].initial = user.email
            self.fields['tel'].initial = user.tel
            self.fields['address'].initial = user.address
            self.fields['password'].initial = user.password
            self.fields['profile_picture'].initial = user.picture
            self.fields['dob'].initial = user.dob

    def save(self, commit=True):
        obj = super().save(commit)

        User.objects.filter(pk=obj.user.pk).update(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            tel=self.cleaned_data['tel'],
            address=self.cleaned_data['address'],
            dob=self.cleaned_data['dob'],
            picture=self.files.get('profile_picture'),
        )
        user = User.objects.filter(pk=obj.user.pk).first()
        obj.user = user
        obj.save()
        return obj


class CustomerCreationForm(BasePersonCreationForm):
    class Meta:
        model = Customer
        exclude = ['user']


class CustomerChangeForm(BasePersonChangeForm):
    class Meta:
        model = Customer
        exclude = ['user', 'password1', 'password2']


class EmployeeCreationForm(BasePersonCreationForm):
    class Meta:
        model = Employee
        exclude = ['user']


class EmployeeChangeForm(BasePersonChangeForm):
    class Meta:
        model = Employee
        exclude = ['user', 'password1', 'password2']
